import datetime

from airflow.macros import ds_add
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.sdk import dag
from common.models.library.library_people_counter import LibraryPeopleCounter
from common.operators.sqlalchemy_operator import sqlalchemy_task


@dag(
    start_date=datetime.datetime(2025, 10, 13),
    schedule="* 2 * * *",
    max_active_runs=5,
    catchup=True,
    tags=["library"],
)
def library_people_counter_dag():
    """A DAG to fetch and store library occupancy data"""

    @sqlalchemy_task(conn_id="superset")
    def transfer_data(session, **context):
        hook_in = PostgresHook(postgres_conn_id="cameras_conn")
        since_date = ds_add(context["ds"], -1)
        sql = f"""SELECT time as date,
                         occupancy,
                         total_in as people_in,
                         total_out as people_out
                FROM public.axis_people_counter
                WHERE camera = '1651' and
                time between '{since_date}' and '{context['ds']}' ORDER BY time asc;"""
        print(sql)
        results = hook_in.get_records(sql)

        for row in results:
            record = LibraryPeopleCounter(
                date=row[0], occupancy=row[1], people_in=row[2], people_out=row[3]
            )
            session.merge(record)
        session.commit()

    transfer_data()


library_people_counter_dag()
