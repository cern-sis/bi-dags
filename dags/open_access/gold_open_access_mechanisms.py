from functools import reduce

import open_access.constants as constants
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
def oa_gold_open_access_mechanisms():
    @task(multiple_outputs=True)
    def generate_params(query, **kwargs):
        year = kwargs["params"].get("year")
        current_collection = "Published+Articles"
        golden_access_base_query = (
            r"(affiliation:CERN+or+595:'For+annual+report')"
            + rf"and+year:{year}+not+980:ConferencePaper+"
            + r"not+980:BookChapter+not+595:'Not+for+annual+report"
        )
        type_of_query = [*query][0]
        query_p = rf"{golden_access_base_query}+{query[type_of_query]}"

        return {
            "endpoint": rf"search?ln=en&cc={current_collection}&p={query_p}"
            + r"&action_search=Search&op1=a&m1=a&p1=&f1=&c="
            + r"Published+Articles&c=&sf=&so=d&rm=&rg=100&sc=0&of=xm",
            "type_of_query": type_of_query,
        }

    @task
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
        {"cern_read_and_publish": constants.CERN_READ_AND_PUBLISH},
        {"cern_individual_apcs": constants.CERN_INDIVIDUAL_APCS},
        {"scoap3": constants.SCOAP3},
        {"other": constants.OTHER},
        {"other_collective_models": constants.OTHER_COLLECTIVE_MODELS},
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

    populate_golden_open_access = PostgresOperator(
        task_id="populate_golden_open_access",
        postgres_conn_id="superset",
        sql="""
        INSERT INTO oa_golden_open_access (year, cern_read_and_publish, cern_individual_apcs,
        scoap3, other, other_collective_models, created_at, updated_at)
        VALUES (%(year)s, %(cern_read_and_publish)s, %(cern_individual_apcs)s,
        %(scoap3)s, %(other)s, %(other_collective_models)s,
        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (year)
        DO UPDATE SET
            cern_read_and_publish = EXCLUDED.cern_read_and_publish,
            cern_individual_apcs = EXCLUDED.cern_individual_apcs,
            scoap3 = EXCLUDED.scoap3,
            other = EXCLUDED.other,
            other_collective_models = EXCLUDED.other_collective_models,
            updated_at = CURRENT_TIMESTAMP;
            """,
        parameters=results,
        executor_config=kubernetes_executor_config,
    )

    counts >> results >> populate_golden_open_access


OA_gold_open_access_mechanisms = oa_gold_open_access_mechanisms()
