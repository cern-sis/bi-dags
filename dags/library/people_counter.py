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
    schedule="@daily",
    catchup=False,
    tags=["library"],
)
def library_people_counter_dag():
    """A DAG to fetch and store library occupancy data"""

    @task()
    def fetch_occupancy(**context):

        start_date = ds_format(ds_add(context["ds"], -1), "%Y-%m-%d", "%Y%m%d")

        params = {
            "start": start_date,
            "end": context["ds_nodash"],
            "resolution": "hour",
        }

        http_hook = HttpHook(
            http_conn_id="people_counter", auth_type=HTTPDigestAuth, method="GET"
        )
        response = http_hook.run_with_advanced_retry(
            endpoint="/a3dpc/api/export_occupancy/json",
            _retry_args={
                "stop": stop_after_attempt(3),
                "retry": retry_if_exception_type(Exception),
            },
            data=params,
        )
        return response.json()

    @sqlalchemy_task(conn_id="superset")
    def populate_occupancy(results, session, **context):

        records = []
        for result in results["data"]:
            records.append(
                LibraryPeopleCounter(
                    date=result["start"],
                    occupancy=result["peak"],
                )
            )
            session.add_all(records)

    populate_occupancy(fetch_occupancy())


library_people_counter_dag()
