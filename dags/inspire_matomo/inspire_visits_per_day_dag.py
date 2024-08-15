import json
import os
from datetime import datetime

import pendulum
from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
from airflow.providers.http.hooks.http import HttpHook
from common.models.inspire_matomo.inspire_matomo import MatomoData
from common.operators.sqlalchemy_operator import sqlalchemy_task
from executor_config import kubernetes_executor_config
from inspire_matomo.utils import get_parameters
from tenacity import retry_if_exception_type, stop_after_attempt

now = datetime.now()
formatted_date = now.strftime("%Y-%m-%d")


@dag(
    start_date=pendulum.today("UTC").add(days=-1),
    schedule="@monthly",
    params={"period": "day", "date": formatted_date},
)
def inspire_visits_per_day_dag():
    @task(executor_config=kubernetes_executor_config)
    def fetch_visits_per_day(**kwargs):
        http_hook = HttpHook(http_conn_id="matomo", method="GET")
        period = kwargs["params"].get("period")
        date = kwargs["params"].get("date")
        parameters = get_parameters(
            period=period, date=date, endpoint_key="visits_per_day"
        )
        token = os.environ.get("MATOMO_AUTH_TOKEN")
        response = http_hook.run_with_advanced_retry(
            endpoint="/index.php",
            data=parameters,
            headers={"Authorization": f"Bearer {token}"},
            _retry_args={
                "stop": stop_after_attempt(3),
                "retry": retry_if_exception_type(AirflowException),
            },
        )
        return response.text

    @task(executor_config=kubernetes_executor_config)
    def fetch_unique_visitors_per_day(**kwargs):
        http_hook = HttpHook(http_conn_id="matomo", method="GET")
        period = kwargs["params"].get("period")
        date = kwargs["params"].get("date")
        parameters = get_parameters(
            period=period, date=date, endpoint_key="unique_visitors"
        )
        token = os.environ.get("MATOMO_AUTH_TOKEN")
        response = http_hook.run_with_advanced_retry(
            endpoint="/index.php",
            data=parameters,
            headers={"Authorization": f"Bearer {token}"},
            _retry_args={
                "stop": stop_after_attempt(3),
                "retry": retry_if_exception_type(AirflowException),
            },
        )
        return response.text

    @sqlalchemy_task(conn_id="superset")
    def populate_database(visits_per_day, unique_visitors_per_day, session, **kwargs):
        visits_per_day_json = json.loads(visits_per_day)
        unique_visitors_per_day_json = json.loads(unique_visitors_per_day)
        date = kwargs["params"].get("date")

        record = (
            session.query(MatomoData)
            .filter_by(date=visits_per_day_json.get("date"))
            .first()
        )
        if record:
            record.visits = int(visits_per_day_json.visits)
            record.unique_visitors = int(unique_visitors_per_day_json.unique_visitors)
        else:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
            new_record = MatomoData(
                visits=int(visits_per_day_json.get("value")),
                unique_visitors=int(unique_visitors_per_day_json.get("value")),
                date=parsed_date,
            )
            session.add(new_record)

    visits_per_day = fetch_visits_per_day()
    unique_visitors_per_day = fetch_unique_visitors_per_day()
    populate_database(
        visits_per_day=visits_per_day,
        unique_visitors_per_day=unique_visitors_per_day,
    )


inspire_visits_per_day = inspire_visits_per_day_dag()
