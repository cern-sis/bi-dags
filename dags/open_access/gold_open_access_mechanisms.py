from functools import reduce

import open_access.constants as constants
import pendulum
from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
from airflow.providers.http.hooks.http import HttpHook
from common.models.open_access.oa_golden_open_access import OAGoldenOpenAccess
from common.operators.sqlalchemy_operator import sqlalchemy_task
from common.utils import get_total_results_count
from executor_config import kubernetes_executor_config
from sqlalchemy.sql import func
from tenacity import retry_if_exception_type, stop_after_attempt


@dag(
    start_date=pendulum.today("UTC").add(days=-1),
    schedule_interval="@monthly",
    params={"year": 2023},
)
def oa_gold_open_access_mechanisms():
    @task(multiple_outputs=True, executor_config=kubernetes_executor_config)
    def generate_params(query_object, **kwargs):
        year = kwargs["params"].get("year")
        current_collection = "Published+Articles"
        golden_access_base_query = (
            r"(affiliation:CERN+or+595:'For+annual+report')"
            + rf"and+year:{year}+not+980:ConferencePaper+"
            + r"not+980:BookChapter+not+595:'Not+for+annual+report"
        )
        type_of_query = [*query_object][0]
        query = rf"{golden_access_base_query}+{query_object[type_of_query]}"

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
        count = get_total_results_count(response.text)
        return {parameters["type_of_query"]: count}

    queries_objects_list = [
        {"cern_read_and_publish": constants.CERN_READ_AND_PUBLISH},
        {"cern_individual_apcs": constants.CERN_INDIVIDUAL_APCS},
        {"scoap3": constants.SCOAP3},
        {"other": constants.OTHER},
        {"other_collective_models": constants.OTHER_COLLECTIVE_MODELS},
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
    def populate_golden_open_access(results, session, **kwargs):
        record = (
            session.query(OAGoldenOpenAccess).filter_by(year=results["year"]).first()
        )
        if record:
            record.cern_read_and_publish = results["cern_read_and_publish"]
            record.cern_individual_apcs = results["cern_individual_apcs"]
            record.scoap3 = results["scoap3"]
            record.other = results["other"]
            record.other_collective_models = results["other_collective_models"]
            record.updated_at = func.now()
        else:
            new_record = OAGoldenOpenAccess(
                year=results["year"],
                cern_read_and_publish=results["cern_read_and_publish"],
                cern_individual_apcs=results["cern_individual_apcs"],
                scoap3=results["scoap3"],
                other=results["other"],
                other_collective_models=results["other_collective_models"],
            )
            session.add(new_record)

    populate_golden_open_access(results)


OA_gold_open_access_mechanisms = oa_gold_open_access_mechanisms()
