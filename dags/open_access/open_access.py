from functools import reduce

import open_access.constants as constants
import open_access.utils as utils
import pendulum
from airflow.decorators import dag, task
from common.models.open_access.open_access import OAOpenAccess
from common.operators.sqlalchemy_operator import sqlalchemy_task
from common.utils import get_total_results_count, request_again_if_failed
from executor_config import kubernetes_executor_config
from sqlalchemy.sql import func


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
        url = utils.get_url(query=f"{base_query}")
        data = request_again_if_failed(url=url)
        total = get_total_results_count(data.text)
        if type_of_query == "gold":
            total = utils.get_golden_access_count(total, url)
        if type_of_query == "green":
            total = utils.get_green_access_count(total, url)
        return {type_of_query: total}

    @task(multiple_outputs=True, executor_config=kubernetes_executor_config)
    def join(values, **kwargs):
        results = reduce(lambda a, b: {**a, **b}, values)
        results["year"] = kwargs["params"].get("year")
        return results

    results = fetch_data_task.expand(
        query=[
            {"closed_access": constants.CLOSED_ACCESS},
            {"bronze_open_access": constants.BRONZE_ACCESS},
            {"green_open_access": constants.GREEN_ACCESS},
            {"gold_open_access": constants.GOLD_ACCESS},
        ],
    )
    unpacked_results = join(results)

    @sqlalchemy_task(conn_id="superset_qa")
    def populate_open_access(results, session, **kwargs):
        record = session.query(OAOpenAccess).filter_by(year=results["year"]).first()
        if record:
            record.closed_access = results["closed_access"]
            record.bronze_open_access = results["bronze_open_access"]
            record.green_open_access = results["green_open_access"]
            record.gold_open_access = results["gold_open_access"]
            record.updated_at = func.now()
        else:
            new_record = OAOpenAccess(
                year=results["year"],
                closed_access=results["closed_access"],
                bronze_open_access=results["bronze_open_access"],
                green_open_access=results["green_open_access"],
                gold_open_access=results["gold_open_access"],
            )
            session.add(new_record)

    populate_open_access(unpacked_results)


OA_dag = oa_dag()
