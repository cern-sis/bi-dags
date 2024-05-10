import logging
import os
from functools import reduce

import pendulum
from airflow.decorators import dag, task
from airflow.providers.postgres.operators.postgres import PostgresOperator
from common.utils import get_total_results_count, request_again_if_failed
from executor_config import kubernetes_executor_config
from library.utils import get_url


@dag(
    start_date=pendulum.today("UTC").add(days=-1),
    schedule="@monthly",
    params={"year": 2023},
)
def library_cern_publication_records_dag():
    @task(executor_config=kubernetes_executor_config)
    def fetch_data_task(key, **kwargs):
        year = kwargs["params"].get("year")
        cds_token = os.environ.get("CDS_TOKEN")
        if not cds_token:
            logging.warning("cds token is not set!")
        type_of_query = key
        url = get_url(type_of_query, year)
        data = request_again_if_failed(url=url, cds_token=cds_token)
        total = get_total_results_count(data.text)
        return {type_of_query: total}

    @task(multiple_outputs=True, executor_config=kubernetes_executor_config)
    def join(values, **kwargs):
        results = reduce(lambda a, b: {**a, **b}, values)
        results["years"] = kwargs["params"].get("year")
        return results

    results = fetch_data_task.expand(
        key=[
            "publications_total_count",
            "conference_proceedings_count",
            "non_journal_proceedings_count",
        ],
    )
    unpacked_results = join(results)

    PostgresOperator(
        task_id="populate_library_cern_publication_records_table",
        postgres_conn_id="superset_qa",
        sql="""
        INSERT INTO library_cern_publication_records (year,
        publications_total_count, conference_proceedings_count,
        non_journal_proceedings_count, created_at, updated_at)
        VALUES (%(years)s, %(publications_total_count)s,
        %(conference_proceedings_count)s, %(non_journal_proceedings_count)s,
        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (year)
        DO UPDATE SET
            publications_total_count = EXCLUDED.publications_total_count,
            conference_proceedings_count = EXCLUDED.conference_proceedings_count,
            non_journal_proceedings_count = EXCLUDED.non_journal_proceedings_count,
            updated_at = CURRENT_TIMESTAMP;
            """,
        parameters={
            "years": unpacked_results["years"],
            "publications_total_count": unpacked_results["publications_total_count"],
            "conference_proceedings_count": unpacked_results[
                "conference_proceedings_count"
            ],
            "non_journal_proceedings_count": unpacked_results[
                "non_journal_proceedings_count"
            ],
        },
        executor_config=kubernetes_executor_config,
    )


library_cern_publication_records = library_cern_publication_records_dag()
