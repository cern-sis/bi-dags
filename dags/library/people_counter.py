import datetime

from airflow.decorators import dag, task
from airflow.macros import ds_add, ds_format
from airflow.providers.http.hooks.http import HttpHook
from common.models.library.library_people_counter import LibraryPeopleCounter
from common.operators.sqlalchemy_operator import sqlalchemy_task
from requests.auth import HTTPDigestAuth
from tenacity import retry_if_exception_type, stop_after_attempt


@dag(
    start_date=datetime.datetime(2024, 11, 28),
    schedule="0 2 * * *",
    max_active_runs=5,
    catchup=True,
    tags=["library"],
)
def library_people_counter_dag():
    """A DAG to fetch and store library occupancy data"""

    http_hook = HttpHook(
        http_conn_id="people_counter", auth_type=HTTPDigestAuth, method="GET"
    )

    @task()
    def set_params(**context):
        end_date = ds_format(ds_add(context["ds"], 1), "%Y-%m-%d", "%Y%m%d")
        return {
            "start": context["ds_nodash"],
            "end": end_date,
            "resolution": "hour",
        }

    @task()
    def fetch_occupancy(query_params):

        response = http_hook.run_with_advanced_retry(
            endpoint="/a3dpc/api/export_occupancy/json",
            _retry_args={
                "stop": stop_after_attempt(3),
                "retry": retry_if_exception_type(Exception),
            },
            data=query_params,
        )
        return response.json()

    @task()
    def fetch_inout(query_params):

        response = http_hook.run_with_advanced_retry(
            endpoint="/a3dpc/api/export/json",
            _retry_args={
                "stop": stop_after_attempt(3),
                "retry": retry_if_exception_type(Exception),
            },
            data=query_params,
        )
        return response.json()

    @sqlalchemy_task(conn_id="superset")
    def populate_database(results_occupancy, results_inout, session, **context):

        records = []

        for occupancy, inout in zip(results_occupancy["data"], results_inout["data"]):
            if not occupancy["peak"] and not inout["in"] and not inout["out"]:
                continue

            occupancy["peak"] = occupancy["peak"] or 0
            inout["in"] = inout["in"] or 0
            inout["out"] = inout["out"] or 0

            records.append(
                LibraryPeopleCounter(
                    date=occupancy["start"],
                    occupancy=occupancy["peak"],
                    people_in=inout["in"],
                    people_out=inout["out"],
                )
            )
            session.add_all(records)

    params = set_params()
    populate_database(fetch_occupancy(params), fetch_inout(params))


library_people_counter_dag()
