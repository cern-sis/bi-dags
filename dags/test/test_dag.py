import logging

import pendulum
from airflow.decorators import dag, task


def fetch(**kwargs):
    return "Test String"


def pull(test_string, **kwargs):
    return test_string


@dag(
    start_date=pendulum.today("UTC").add(days=-1),
    schedule="@hourly",
    params={"from_date": None, "until_date": None, "per_page": None},
)
def test_dag():
    @task()
    def fetch_task(**kwargs):
        return fetch()

    @task()
    def pull_task(test_string, **kwargs):
        logging.info(f"The value from previous task is: {test_string}")
        return pull

    value = fetch_task()
    pull_task(value)


Test_dag = test_dag()
