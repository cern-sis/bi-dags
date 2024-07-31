from functools import reduce

import open_access.constants as constants
import open_access.utils as utils
import pendulum
from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
from airflow.providers.http.hooks.http import HttpHook
from common.models.open_access.open_access import OAOpenAccess
from common.operators.sqlalchemy_operator import sqlalchemy_task
from common.utils import get_total_results_count
from executor_config import kubernetes_executor_config
from sqlalchemy.sql import func
from tenacity import retry_if_exception_type, stop_after_attempt


@dag(
    start_date=pendulum.today("UTC").add(days=-1),
    schedule="@monthly",
    params={"year": 2023},
)
def oa_dag():
    @task(multiple_outputs=True, executor_config=kubernetes_executor_config)
    def generate_params(query_object, **kwargs):
        year = kwargs["params"].get("year")
        current_collection = "Published+Articles"
        base_query = (
            r"(affiliation:CERN+or+595:'For+annual+report')"
            + rf"and+year:{year}+not+980:ConferencePaper+"
            + r"not+980:BookChapter"
        )
        type_of_query = [*query_object][0]
        query = rf"{base_query}+{query_object[type_of_query]}"

        return {
            "endpoint": rf"search?ln=en&cc={current_collection}&p={query}"
            + r"&action_search=Search&op1=a&m1=a&p1=&f1=&c="
            + r"Published+Articles&c=&sf=&so=d&rm=&rg=100&sc=0&of=xm",
            "type_of_query": type_of_query,
        }

    @task(executor_config=kubernetes_executor_config)
    def fetch_count(parameters):
        http_hook = HttpHook(http_conn_id="cds", method="GET")
        response = http_hook.run_with_advanced_retry(
            endpoint=parameters["endpoint"],
            _retry_args={
                "stop": stop_after_attempt(3),
                "retry": retry_if_exception_type(AirflowException),
            },
        )
        type_of_query = parameters["type_of_query"]
        endpoint = parameters["endpoint"]
        count = get_total_results_count(response.text)
        if type_of_query == "gold_open_access":
            total_gold = utils.get_golden_access_count(count, endpoint)
            return {parameters["type_of_query"]: total_gold}
        elif type_of_query == "green_open_access":
            total_green = utils.get_green_access_count(count, endpoint)
            return {parameters["type_of_query"]: total_green}
        return {parameters["type_of_query"]: count}

    queries_objects_list = [
        {"closed_access": constants.CLOSED_ACCESS},
        {"bronze_open_access": constants.BRONZE_ACCESS},
        {"green_open_access": constants.GREEN_ACCESS},
        {"gold_open_access": constants.GOLD_ACCESS},
    ]

    parameters = generate_params.expand(query_object=queries_objects_list)
    counts = fetch_count.expand(parameters=parameters)

    @task(multiple_outputs=True, executor_config=kubernetes_executor_config)
    def join_and_add_year(counts, **kwargs):
        year = kwargs["params"].get("year")
        results = reduce(lambda a, b: {**a, **b}, counts)
        results["year"] = year
        return results

    results = join_and_add_year(counts)

    @sqlalchemy_task(conn_id="superset")
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

    populate_open_access(results)


OA_dag = oa_dag()
