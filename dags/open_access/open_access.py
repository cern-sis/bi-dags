import logging

import open_access.constants as constants
import pendulum
from airflow.decorators import dag, task
from common.models.open_access.open_access import OAOpenAccess
from common.operators.sqlalchemy_operator import sqlalchemy_task
from executor_config import kubernetes_executor_config
from open_access.utils import (
    fetch_count_from_comments,
    fetch_count_from_parsed_records,
    generate_params,
    get_golden_access_count,
    get_green_access_count,
)
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)


@dag(
    start_date=pendulum.today("UTC").add(days=-1),
    schedule="@monthly",
    params={"year": 2023},
)
def oa_dag():
    @task(executor_config=kubernetes_executor_config)
    def fetch_closed_access_count(query_object, **kwargs):
        year = kwargs["params"].get("year")
        parameters = generate_params(query_object, year)
        logger.info(f"Query: {parameters}")
        return fetch_count_from_comments(parameters=parameters)

    @task(executor_config=kubernetes_executor_config)
    def fetch_bronze_open_access_count(query_object, closed_access, **kwargs):
        year = kwargs["params"].get("year")
        parameters = generate_params(query_object, year)
        logger.info(f"Query: {parameters}")
        return fetch_count_from_comments(parameters=parameters, previous=closed_access)

    @task(executor_config=kubernetes_executor_config)
    def fetch_gold_open_access_count(query_object, bronze_access, **kwargs):
        year = kwargs["params"].get("year")
        parameters = generate_params(query_object, year)
        logger.info(f"Query: {parameters}")
        return fetch_count_from_parsed_records(
            parameters=parameters,
            count_function=get_golden_access_count,
            previous=bronze_access,
        )

    @task(executor_config=kubernetes_executor_config)
    def fetch_green_open_access_count(query_object, gold_access, **kwargs):
        year = kwargs["params"].get("year")
        parameters = generate_params(query_object, year)
        logger.info(f"Query: {parameters}")
        return fetch_count_from_parsed_records(
            parameters=parameters,
            count_function=get_green_access_count,
            previous=gold_access,
        )

    closed_access = fetch_closed_access_count(
        {"closed_access": constants.CLOSED_ACCESS}
    )
    closed_bronze_access = fetch_bronze_open_access_count(
        {"bronze_open_access": constants.BRONZE_ACCESS}, closed_access
    )
    closed_bronze_gold_access = fetch_gold_open_access_count(
        {"gold_open_access": constants.GOLD_ACCESS}, closed_bronze_access
    )
    closed_bronze_gold_green_access = fetch_green_open_access_count(
        {"green_open_access": constants.GREEN_ACCESS}, closed_bronze_gold_access
    )

    @task(executor_config=kubernetes_executor_config)
    def add_year(closed_bronze_gold_green_access, **kwargs):
        year = kwargs["params"].get("year")
        closed_bronze_gold_green_access["year"] = year
        return closed_bronze_gold_green_access

    results = add_year(closed_bronze_gold_green_access)

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
