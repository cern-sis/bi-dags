import os

import pendulum
from airflow.models import DAG
from airflow.models.param import Param
from airflow_provider_alembic.operators.alembic import AlembicOperator

with DAG(
    "migrations",
    schedule=None,
    start_date=pendulum.today("UTC").add(days=-1),
    params={"command": Param("upgrade"), "revision": Param("head")},
) as dag:
    AlembicOperator(
        task_id="alembic_op",
        conn_id="superset_qa",
        command="{{ params.command }}",
        revision="{{ params.revision }}",
        script_location=f"{os.environ['AIRFLOW_HOME']}/dags/migrations/",
    )
