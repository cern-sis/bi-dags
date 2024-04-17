from functools import reduce

import open_access.utils as utils
import pendulum
from airflow.decorators import dag, task
from airflow.providers.postgres.operators.postgres import PostgresOperator
from executor_config import kubernetes_executor_config


@dag(
    start_date=pendulum.today("UTC").add(days=-1),
    schedule="@monthly",
    params={"year": 2023},
)
def oa_dag():
    @task(executor_config=kubernetes_executor_config)
    def fetch_data_task(query, **kwargs):
        year = kwargs["params"].get("year")
        base_query = (
            r"(affiliation:CERN+or+595:'For+annual+report')"
            + rf"and+year:{year}+not+980:ConferencePaper+"
            + r"not+980:BookChapter"
        )
        type_of_query = [*query][0]
        url = utils.get_url(f"{base_query}+{query[type_of_query]}")
        data = utils.get_data(url)
        total = utils.get_total_results_count(data.text)
        return {type_of_query: total}

    @task(multiple_outputs=True, executor_config=kubernetes_executor_config)
    def join(values, **kwargs):
        results = reduce(lambda a, b: {**a, **b}, values)
        results["years"] = kwargs["params"].get("year")
        return results

    results = fetch_data_task.expand(
        query=[
            {"closed": utils.closed_access_query},
            {"bronze": utils.bronze_access_query},
            {"green": utils.green_access_query},
            {"gold": utils.gold_access_query},
        ],
    )

    unpacked_results = join(results)

    PostgresOperator(
        task_id="populate_open_access_table",
        postgres_conn_id="superset_qa",
        sql="""
        SET search_path TO oa;
        INSERT INTO "oa.open_access" (year, closed_access, bronze_open_access,
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
