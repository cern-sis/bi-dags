import logging
import os
from functools import reduce

import pendulum
from airflow.decorators import dag, task
from common.models.library.library_cern_publication_records import (
    LibraryCernPublicationRecords,
)
from common.operators.sqlalchemy_operator import sqlalchemy_task
from common.utils import get_total_results_count, request_again_if_failed
from executor_config import kubernetes_executor_config
from library.utils import get_url
from sqlalchemy.sql import func


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
        results["year"] = kwargs["params"].get("year")
        return results

    results = fetch_data_task.expand(
        key=[
            "publications_total_count",
            "conference_proceedings_count",
            "non_journal_proceedings_count",
        ],
    )
    unpacked_results = join(results)

    @sqlalchemy_task(conn_id="superset_qa")
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

    populate_cern_publication_records(unpacked_results)


library_cern_publication_records = library_cern_publication_records_dag()
