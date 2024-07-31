from functools import reduce

import pendulum
from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
from airflow.providers.http.hooks.http import HttpHook
from common.models.library.library_cern_publication_records import (
    LibraryCernPublicationRecords,
)
from common.operators.sqlalchemy_operator import sqlalchemy_task
from common.utils import get_total_results_count
from executor_config import kubernetes_executor_config
from library.utils import get_endpoint
from sqlalchemy.sql import func
from tenacity import retry_if_exception_type, stop_after_attempt


@dag(
    start_date=pendulum.today("UTC").add(days=-1),
    schedule="@monthly",
    params={"year": 2023},
)
def library_cern_publication_records_dag():
    @task(multiple_outputs=True, executor_config=kubernetes_executor_config)
    def generate_params(key, **kwargs):
        year = kwargs["params"].get("year")
        url = get_endpoint(key, year)
        return {
            "endpoint": url,
            "type_of_query": key,
        }

    @task(executor_config=kubernetes_executor_config)
    def fetch_count(parameters):
        http_hook = HttpHook(http_conn_id="cds", method="GET")
        response = http_hook.run_with_advanced_retry(
            endpoint=parameters["endpoint"],
            _retry_args={
                "stop": stop_after_attempt(3),
                "retry": retry_if_exception_type(AirflowException),
            },
        )
        count = get_total_results_count(response.text)
        return {parameters["type_of_query"]: count}

    keys_list = [
        "publications_total_count",
        "conference_proceedings_count",
        "non_journal_proceedings_count",
    ]

    parameters = generate_params.expand(key=keys_list)
    counts = fetch_count.expand(parameters=parameters)

    @task(multiple_outputs=True, executor_config=kubernetes_executor_config)
    def join_and_add_year(counts, **kwargs):
        year = kwargs["params"].get("year")
        results = reduce(lambda a, b: {**a, **b}, counts)
        results["year"] = year
        return results

    results = join_and_add_year(counts)

    @sqlalchemy_task(conn_id="superset")
    def populate_cern_publication_records(results, session, **kwargs):
        record = (
            session.query(LibraryCernPublicationRecords)
            .filter_by(year=results["year"])
            .first()
        )
        if record:
            record.publications_total_count = results["publications_total_count"]
            record.conference_proceedings_count = results[
                "conference_proceedings_count"
            ]
            record.non_journal_proceedings_count = results[
                "non_journal_proceedings_count"
            ]
            record.updated_at = func.now()
        else:
            new_record = LibraryCernPublicationRecords(
                year=results["year"],
                publications_total_count=results["publications_total_count"],
                conference_proceedings_count=results["conference_proceedings_count"],
                non_journal_proceedings_count=results["non_journal_proceedings_count"],
            )
            session.add(new_record)

    populate_cern_publication_records(results)


library_cern_publication_records = library_cern_publication_records_dag()
