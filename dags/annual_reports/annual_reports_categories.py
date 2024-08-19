from datetime import datetime

import pendulum
from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
from airflow.providers.http.hooks.http import HttpHook
from annual_reports.utils import get_endpoint, get_subjects_by_year
from common.models.annual_reports.annual_reports import Categories
from common.operators.sqlalchemy_operator import sqlalchemy_task
from executor_config import kubernetes_executor_config
from sqlalchemy.sql import func
from tenacity import retry_if_exception_type, stop_after_attempt

current_year = datetime.now().year
years = list(range(2004, current_year + 1))


@dag(
    start_date=pendulum.today("UTC").add(days=-1),
    schedule="0 0 */15 * *",
)
def annual_reports_categories_dag():
    @task(executor_config=kubernetes_executor_config)
    def fetch_categories_report_count(year, **kwargs):
        endpoint = get_endpoint(year=year, key="subjects")
        http_hook = HttpHook(http_conn_id="cds", method="GET")
        response = http_hook.run_with_advanced_retry(
            endpoint=endpoint,
            _retry_args={
                "stop": stop_after_attempt(3),
                "retry": retry_if_exception_type(AirflowException),
            },
        )
        subjects = get_subjects_by_year(response.content)
        return {year: subjects}

    @sqlalchemy_task(conn_id="superset")
    def populate_categories_report_count(entry, session, **kwargs):
        for year, subjects in entry.items():
            full_date_str = f"{year}-01-01"
            year_date = datetime.strptime(full_date_str, "%Y-%m-%d").date()
            for category, count in subjects.items():
                record = (
                    session.query(Categories)
                    .filter_by(category=category, year=year_date)
                    .first()
                )
                if record:
                    record.count = int(count)
                    record.year = year_date
                    record.updated_at = func.now()
                else:
                    new_record = Categories(
                        year=year_date,
                        category=category,
                        count=int(count),
                    )
                    session.add(new_record)

    previous_task = None
    for year in years:
        fetch_task = fetch_categories_report_count.override(
            task_id=f"fetch_report_{year}"
        )(year=year)
        populate_task = populate_categories_report_count.override(
            task_id=f"populate_report_{year}"
        )(entry=fetch_task)
        if previous_task:
            previous_task >> fetch_task
        fetch_task >> populate_task
        previous_task = populate_task


annual_reports_categories = annual_reports_categories_dag()
