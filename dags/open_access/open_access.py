import logging
import os
from functools import reduce

import open_access.constants as constants
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
        cds_token = os.environ.get("CDS_TOKEN")
        if not cds_token:
            logging.warning("cds token is not set!")
        base_query = (
            r"(affiliation:CERN+or+595:'For+annual+report')"
            + rf"and+year:{year}+not+980:ConferencePaper+"
            + r"not+980:BookChapter"
        )
        type_of_query = [*query][0]
        url = utils.get_url(
            query=f"{base_query}+{query[type_of_query]}", cds_token=cds_token
        )
        data = utils.request_again_if_failed(url)
        total = utils.get_total_results_count(data.text)
        if type_of_query == "gold":
            total = utils.get_gold_access_count(total, url)
        if type_of_query == "green":
            total = total - utils.get_gold_access_count(total, url)
        return {type_of_query: total}

    @task(multiple_outputs=True, executor_config=kubernetes_executor_config)
    def join(values, **kwargs):
        results = reduce(lambda a, b: {**a, **b}, values)
        results["years"] = kwargs["params"].get("year")
        return results

    results = fetch_data_task.expand(
        query=[
            {"closed": constants.CLOSED_ACCESS},
            {"bronze": constants.BRONZE_ACCESS},
            {"green": constants.GREEN_ACCESS},
            {"gold": constants.GOLD_ACCESS},
        ],
    )
    unpacked_results = join(results)

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
