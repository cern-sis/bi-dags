from functools import reduce

import library.constants as constants
import pendulum
from airflow.decorators import dag, task
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from common.utils import get_total_results_count
from executor_config import kubernetes_executor_config
from tenacity import retry_if_exception_type, stop_after_attempt


@dag(
    start_date=pendulum.today("UTC").add(days=-1),
    schedule_interval="@monthly",
    params={"year": 2023},
)
def library_new_items_in_the_institutional_repository():
    @task(executor_config=kubernetes_executor_config, multiple_outputs=True)
    def generate_params(query, **kwargs):
        year = kwargs["params"].get("year")
        base_query = f"search?ln=en&p=year%3A{year}+"
        type_of_query = [*query][0]
        return {
            "endpoint": base_query + query[type_of_query],
            "type_of_query": type_of_query,
        }

    @task(executor_config=kubernetes_executor_config)
    def fetch_count(parameters):
        http_hook = HttpHook(http_conn_id="cds", method="GET")
        response = http_hook.run_with_advanced_retry(
            endpoint=parameters["endpoint"],
            _retry_args={
                "stop": stop_after_attempt(3),
                "retry": retry_if_exception_type(Exception),
            },
        )
        count = get_total_results_count(response.text)
        return {parameters["type_of_query"]: count}

    query_list = [
        {"inspire_arxiv_records": constants.INSPIRE_ARXIV_RECORDS},
        {"inspire_curators_records": constants.INSPIRE_CURATORS_RECORDS},
    ]

    parameters = generate_params.expand(query=query_list)
    counts = fetch_count.expand(parameters=parameters)

    @task(multiple_outputs=True, executor_config=kubernetes_executor_config)
    def join_and_add_year(counts, **kwargs):
        year = kwargs["params"].get("year")
        results = reduce(lambda a, b: {**a, **b}, counts)
        results["year"] = year
        return results

    results = join_and_add_year(counts)

    populate_items_in_the_institutional_repository = PostgresOperator(
        task_id="populate_items_in_the_institutional_repository",
        postgres_conn_id="superset_qa",
        sql="""
        INSERT INTO items_in_the_institutional_repository (year,
        inspire_arxiv_records, inspire_curators_records, created_at, updated_at)
        VALUES (%(year)s, %(inspire_arxiv_records)s, %(inspire_curators_records)s,
        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (year)
        DO UPDATE SET
            inspire_arxiv_records = EXCLUDED.inspire_arxiv_records,
            inspire_curators_records = EXCLUDED.inspire_curators_records,
            updated_at = CURRENT_TIMESTAMP;
            """,
        parameters=results,
        executor_config=kubernetes_executor_config,
    )

    counts >> results >> populate_items_in_the_institutional_repository


Library_new_items_in_the_institutional_repository = (
    library_new_items_in_the_institutional_repository()
)
