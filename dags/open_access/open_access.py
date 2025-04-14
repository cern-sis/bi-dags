import logging

import open_access.constants as constants
import pendulum
from airflow.decorators import dag, task
from common.models.open_access.open_access import OAOpenAccess
from common.operators.sqlalchemy_operator import sqlalchemy_task
from executor_config import kubernetes_executor_config
from open_access.utils import (
    fetch_count_from_comments,
    get_url,
)
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)


@dag(
    start_date=pendulum.today("UTC").add(days=-1),
    schedule="@monthly",
    params={"year": pendulum.now("UTC").year},
)
def oa_dag():

    @task(executor_config=kubernetes_executor_config)
    def fetch_closed_access_count(query, **kwargs):
        year = kwargs["params"].get("year")
        query = query.format(year=year)
        logger.info(f"Query: {query}")
        endpoint = get_url(query)

        logger.info(f"Endpoint: {endpoint}")
        return fetch_count_from_comments(endpoint)

    @task(executor_config=kubernetes_executor_config)
    def fetch_bronze_access_count(query, **kwargs):
        year = kwargs["params"].get("year")
        query = query.format(year=year)
        logger.info(f"Query: {query}")
        endpoint = get_url(query)

        logger.info(f"Endpoint: {endpoint}")
        return fetch_count_from_comments(endpoint)

    @task(executor_config=kubernetes_executor_config)
    def fetch_gold_access_count(query, **kwargs):
        year = kwargs["params"].get("year")
        query = query.format(year=year)
        logger.info(f"Query: {query}")
        endpoint = get_url(query)

        logger.info(f"Endpoint: {endpoint}")
        return fetch_count_from_comments(endpoint)

    @task(executor_config=kubernetes_executor_config)
    def fetch_green_access_count(query, **kwargs):
        year = kwargs["params"].get("year")
        query = query.format(year=year)
        logger.info(f"Query: {query}")
        endpoint = get_url(query)

        logger.info(f"Endpoint: {endpoint}")
        return fetch_count_from_comments(endpoint)

    closed_access = fetch_closed_access_count(constants.CLOSED_OPEN_ACCESS_QUERY)
    bronze_open_access = fetch_bronze_access_count(constants.BRONZE_OPEN_ACCESS_QUERY)
    gold_open_access = fetch_gold_access_count(constants.GOLD_OPEN_ACCESS_QUERY)
    green_open_access = fetch_green_access_count(constants.GREEN_OPEN_ACCESS_QUERY)
    results = {
        "closed_access": closed_access,
        "bronze_open_access": bronze_open_access,
        "gold_open_access": gold_open_access,
        "green_open_access": green_open_access,
    }

    @task(executor_config=kubernetes_executor_config)
    def add_year(results, **kwargs):
        year = kwargs["params"].get("year")
        results["year"] = year
        return results

    results = add_year(results)

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
