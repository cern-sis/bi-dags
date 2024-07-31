from functools import reduce

import library.constants as constants
import pendulum
from airflow.decorators import dag, task
from airflow.providers.http.hooks.http import HttpHook
from common.models.library.library_new_items_in_the_institutional_repository import (
    LibraryNewItemsInTheInstitutionalRepository,
)
from common.operators.sqlalchemy_operator import sqlalchemy_task
from common.utils import get_total_results_count
from executor_config import kubernetes_executor_config
from sqlalchemy.sql import func
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

    @sqlalchemy_task(conn_id="superset")
    def populate_new_items_in_the_institutional_repository(results, session, **kwargs):
        record = (
            session.query(LibraryNewItemsInTheInstitutionalRepository)
            .filter_by(year=results["year"])
            .first()
        )
        if record:
            record.inspire_arxiv_records = results["inspire_arxiv_records"]
            record.inspire_curators_records = results["inspire_curators_records"]
            record.updated_at = func.now()
        else:
            new_record = LibraryNewItemsInTheInstitutionalRepository(
                year=results["year"],
                inspire_arxiv_records=results["inspire_arxiv_records"],
                inspire_curators_records=results["inspire_curators_records"],
            )
            session.add(new_record)

    populate_new_items_in_the_institutional_repository(results)


Library_new_items_in_the_institutional_repository = (
    library_new_items_in_the_institutional_repository()
)
