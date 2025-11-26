import datetime

from airflow.macros import ds_add
from airflow.models import Variable
from airflow.providers.http.hooks.http import HttpHook
from airflow.sdk import dag
from common.models.library.library_catalog_metrics import LibraryCatalogMetrics
from common.operators.sqlalchemy_operator import sqlalchemy_task


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
    def populate_data(category, filter, session, **context):

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

        records = []
        for agg_name, agg_items in response.json()["aggregations"].items():
            if "buckets" not in agg_items:
                continue
            for bucket in agg_items["buckets"]:
                records.append(
                    LibraryCatalogMetrics(
                        date=context["ds"],
                        filter=filter,
                        category=category,
                        aggregation=agg_name,
                        key=bucket["key"],
                        value=bucket["doc_count"],
                    )
                )
        session.add_all(records)

    @sqlalchemy_task(conn_id="superset")
    def collect_ils_record_changes(session, **context):
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

        hook = HttpHook(
            http_conn_id="library_catalog_conn",
            method="POST",
        )

        response = hook.run(
            endpoint="api/stats",
            json=data,
            headers={"Authorization": f"Bearer {Variable.get('CATALOG_API_TOKEN')}"},
        )

        records = []
        for _, metric_data in response.json().items():
            for bucket in metric_data["buckets"]:
                records.append(
                    LibraryCatalogMetrics(
                        date=date_to_fetch,
                        filter="ils_record_changes",
                        category="api/stats",
                        aggregation=bucket["pid_type"],
                        key=bucket["method"],
                        value=int(bucket["count"]),
                    )
                )
        session.add_all(records)

    populate_data("items", "status:CAN_CIRCULATE")
    populate_data("circulation/loans", None)
    collect_ils_record_changes()


library_catalog_metrics()
