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
def oa_gold_open_access_mechanisms():
    @task(executor_config=kubernetes_executor_config)
    def fetch_data_task(query, **kwargs):
        year = kwargs["params"].get("year")
        golden_access_base_query = (
            r"(affiliation:CERN+or+595:'For+annual+report')"
            + rf"and+year:{year}+not+980:ConferencePaper+"
            + r"not+980:BookChapter+not+595:'Not+for+annual+report"
        )
        type_of_query = [*query][0]
        url = utils.get_url(f"{golden_access_base_query}+{query[type_of_query]}")
        data = utils.request_again_if_failed(url)
        total = utils.get_total_results_count(data.text)
        return {type_of_query: total}

    @task(multiple_outputs=True, executor_config=kubernetes_executor_config)
    def join(values, **kwargs):
        results = reduce(lambda a, b: {**a, **b}, values)
        results["years"] = kwargs["params"].get("year")
        return results

    results = fetch_data_task.expand(
        query=[
            {"cern_read_and_publish": utils.cern_read_and_publish},
            {"cern_individual_apcs": utils.cern_individual_apcs},
            {"scoap3": utils.scoap3},
            {"other": utils.other},
            {"other_collective_models": utils.other_collective_models},
        ],
    )
    unpacked_results = join(results)

    PostgresOperator(
        task_id="populate_golden_open_access",
        postgres_conn_id="superset_qa",
        sql="""
        INSERT INTO oa_golden_open_access (year, cern_read_and_publish, cern_individual_apcs,
        scoap3, other, other_collective_models, created_at, updated_at)
        VALUES (%(years)s, %(cern_read_and_publish)s, %(cern_individual_apcs)s,
        %(scoap3)s, %(other)s, %(other_collective_models)s,
        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (year)
        DO UPDATE SET
            cern_read_and_publish = EXCLUDED.cern_read_and_publish,
            cern_individual_apcs = EXCLUDED.cern_individual_apcs,
            scoap3 = EXCLUDED.scoap3,
            other = EXCLUDED.other,
            other_collective_models = EXCLUDED.other_collective_models,
            updated_at = CURRENT_TIMESTAMP;
            """,
        parameters={
            "years": unpacked_results["years"],
            "cern_read_and_publish": unpacked_results["cern_read_and_publish"],
            "cern_individual_apcs": unpacked_results["cern_individual_apcs"],
            "scoap3": unpacked_results["scoap3"],
            "other": unpacked_results["other"],
            "other_collective_models": unpacked_results["other_collective_models"],
        },
        executor_config=kubernetes_executor_config,
    )


OA_gold_open_access_mechanisms = oa_gold_open_access_mechanisms()
