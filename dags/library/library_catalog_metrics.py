import datetime

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

    populate_data("items", "status:CAN_CIRCULATE")
    populate_data("circulation/loans", None)


library_catalog_metrics()
