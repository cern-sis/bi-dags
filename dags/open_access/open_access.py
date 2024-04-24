from functools import reduce

import pendulum
from airflow.decorators import dag, task
from airflow.providers.postgres.operators.postgres import PostgresOperator
from executor_config import kubernetes_executor_config
from open_access.open_access_api import OpenAccessApi


@dag(
    start_date=pendulum.today("UTC").add(days=-1),
    schedule="@monthly",
    params={"year": 2023},
)
def oa_dag():
    @task(executor_config=kubernetes_executor_config)
    def set_a_year(**kwargs):
        year = kwargs["params"].get("year")
        return OpenAccessApi(year=year)

    @task(executor_config=kubernetes_executor_config)
    def fetch_closed_access(api, **kwargs):
        return api.get_closed_access_total_count()

    @task(executor_config=kubernetes_executor_config)
    def fetch_bronze_access(api, **kwargs):
        return api.get_bronze_access_total_count()

    @task(executor_config=kubernetes_executor_config)
    def fetch_green_access(api, **kwargs):
        return api.get_green_access_total_count()

    @task(executor_config=kubernetes_executor_config)
    def fetch_gold_access(api, **kwargs):
        return api.get_gold_access_total_count()

    @task(executor_config=kubernetes_executor_config)
    def join(values, **kwargs):
        results = reduce(lambda a, b: {**a, **b}, values)
        results["years"] = kwargs["params"].get("year")
        return results

    api = set_a_year()
    closed_access_count = fetch_closed_access(api)
    closed_bronze_count = fetch_bronze_access(api)
    closed_green__count = fetch_green_access(api)
    closed_gold_count = fetch_gold_access(api)

    unpacked_results = join(
        [
            closed_access_count,
            closed_bronze_count,
            closed_green__count,
            closed_gold_count,
        ]
    )

    PostgresOperator(
        task_id="populate_open_access_table",
        postgres_conn_id="superset_qa",
        sql="""
        INSERT INTO oa_open_access (year, closed_access, bronze_open_access,
        green_open_access, gold_open_access, created_at, updated_at)
        VALUES (%(years)s, %(closed)s, %(bronze)s, %(green)s, %(gold)s,
        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (year)
        DO UPDATE SET
            closed_access = EXCLUDED.closed_access,
            bronze_open_access = EXCLUDED.bronze_open_access,
            green_open_access = EXCLUDED.green_open_access,
            gold_open_access = EXCLUDED.gold_open_access,
            updated_at = CURRENT_TIMESTAMP;
            """,
        parameters={
            "years": unpacked_results["years"],
            "closed": unpacked_results["closed"],
            "bronze": unpacked_results["bronze"],
            "green": unpacked_results["green"],
            "gold": unpacked_results["gold"],
        },
        executor_config=kubernetes_executor_config,
    )


OA_dag = oa_dag()
