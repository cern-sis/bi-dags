import datetime
import json
import logging

from airflow.macros import ds_add
from airflow.models import Variable
from airflow.providers.http.hooks.http import HttpHook
from airflow.sdk import dag
from common.models.library.library_catalog_metrics import LibraryCatalogMetrics
from common.operators.sqlalchemy_operator import sqlalchemy_task
from library.utils import (
    aggregation_walker,
    set_hist_library_catalog,
    set_stat_library_catalog,
)

logger = logging.getLogger(__name__)


@dag(
    start_date=datetime.datetime(2021, 4, 15),
    schedule="0 2 * * *",
    max_active_runs=5,
    catchup=False,
    tags=["library"],
)
def library_catalog_metrics():
    """A DAG to fetch and store library occupancy data"""

    @sqlalchemy_task(conn_id="superset")
    def populate_data(note, category, filter, session, **context):

        logger.info("Fetching data for %s", note)
        hook = HttpHook(
            http_conn_id="library_catalog_conn",
            method="GET",
        )
        data = {"size": 1}
        if filter:
            data["q"] = filter

        response = hook.run(
            endpoint=f"api/{category}/",
            data=data,
            headers={"Authorization": f"Bearer {Variable.get('CATALOG_API_TOKEN')}"},
        )

        date_to_fetch = ds_add(context["ds"], -1)

        records = []

        transformed_aggregations = aggregation_walker(response.json()["aggregations"])

        for agg_name, key_values in transformed_aggregations.items():
            for key, value in key_values.items():
                records.append(
                    LibraryCatalogMetrics(
                        date=date_to_fetch,
                        filter=filter,
                        category=category,
                        aggregation=agg_name,
                        key=key,
                        value=value,
                        note=note,
                    )
                )
        session.add_all(records)

    @sqlalchemy_task(conn_id="superset")
    def populate_data_hist(
        note, endpoint, filter, group_by, metrics, session, **context
    ):
        logger.info("Fetching data for %s", note)

        date_to_fetch = ds_add(context["ds"], -1)
        data = {}

        if filter:
            data["q"] = filter
        else:
            data["q"] = f"_created:[{date_to_fetch} TO {date_to_fetch}]"
        if group_by:
            data["group_by"] = json.dumps(group_by)
        if metrics:
            data["metrics"] = json.dumps(metrics)

        set_hist_library_catalog(
            note, endpoint, data, date_to_fetch, data.get("q"), session
        )

    @sqlalchemy_task(conn_id="superset")
    def populate_data_stats(note, stat, params, session, **context):
        logger.info("Fetching data for %s", note)

        date_to_fetch = ds_add(context["ds"], -1)
        data = {
            stat: {
                "stat": stat,
                "params": {
                    "start_date": date_to_fetch,
                    "end_date": date_to_fetch,
                    "interval": "day",
                    **params,
                },
            }
        }

        set_stat_library_catalog(note, stat, data, date_to_fetch, session)

    @sqlalchemy_task(conn_id="superset")
    def collect_ils_record_changes(session, **context):
        logger.info("Fetching data for 4")

        methods = ["insert", "update", "delete"]
        pid_types = [
            "acqoid",
            "dreqid",
            "eitmid",
            "illbid",
            "ilocid",
            "pitmid",
            "locid",
            "provid",
            "docid",
            "serid",
        ]

        data = {}

        date_to_fetch = ds_add(context["ds"], -1)

        for pid_type in pid_types:
            for method in methods:
                data[f"{pid_type}_{method}"] = {
                    "stat": "ils-record-changes",
                    "params": {
                        "start_date": date_to_fetch,
                        "end_date": date_to_fetch,
                        "method": method,
                        "pid_type": pid_type,
                        "interval": "day",
                    },
                }
        set_stat_library_catalog(
            "4", "ils_record_changes", data, date_to_fetch, session
        )

    populate_data_hist(
        "1Q1",
        "circulation/loans/stats",
        None,
        [{"field": "_created", "interval": "1d"}],
        None,
    )
    populate_data_stats("1Q2", "loan-transitions", params={"trigger": "extend"})
    populate_data("1Q3", "items", "status:CAN_CIRCULATE")
    populate_data_hist(
        "2",
        "circulation/loans/stats",
        None,
        [{"field": "start_date", "interval": "1d"}],
        [{"field": "extra_data.stats.loan_duration", "aggregation": "avg"}],
    )
    populate_data_hist(
        "3.1",
        "circulation/loans/stats",
        "delivery.method:SELF-CHECKOUT",
        [{"field": "_created", "interval": "1d"}],
        None,
    )
    populate_data_hist(
        "3.2",
        "circulation/loans/stats",
        None,
        [
            {"field": "_created", "interval": "1M"},
            {"field": "extra_data.stats.available_items_during_request"},
        ],
        [{"field": "extra_data.stats.waiting_time", "aggregation": "avg"}],
    )
    populate_data_hist(
        "3.5.1",
        "acquisition/stats",
        None,
        [{"field": "_created", "interval": "1d"}],
        [{"field": "stats.document_request_waiting_time", "aggregation": "avg"}],
    )
    populate_data_hist(
        "3.5.2",
        "acquisition/stats",
        None,
        [{"field": "_created", "interval": "1d"}],
        [{"field": "stats.order_processing_time", "aggregation": "avg"}],
    )
    populate_data_hist(
        "3.5.3",
        "document-requests/stats",
        None,
        [{"field": "_created", "interval": "1d"}],
        [{"field": "stats.order_processing_time", "aggregation": "avg"}],
    )
    populate_data("3.5.4", "document-requests", None)

    collect_ils_record_changes()
    populate_data_hist(
        "5.2",
        "circulation/loans/stats",
        None,
        [{"field": "patron.department.keyword"}],
        None,
    )
    populate_data("6", "circulation/loans", None)


library_catalog_metrics()
