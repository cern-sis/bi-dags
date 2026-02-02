from airflow.models import Variable
from airflow.providers.http.hooks.http import HttpHook
from common.models.library.library_catalog_metrics import LibraryCatalogMetrics


def get_endpoint(key, year):
    endpoint = {
        "publications_total_count": r"search?wl=0&ln=en&cc=Published+"
        + r"Articles&sc=1&p=%28affiliation%3ACERN+or+595%3A%27For+annual+report%27%29+and+"
        + rf"year%3A{year}+not+980%3AConferencePaper+not+980%3ABookChapter+not+595%3A%27Not+"
        + r"for+annual+report%27&f=&action_search=Search&of=xm",
        "conference_proceedings_count": r"search?wl=0&ln=en&cc=Published+"
        + r"Articles&p=980%3AARTICLE+and+%28affiliation%3ACERN+or+595%3A%27For+annual+report%27%29+"
        + rf"and+year%3A{year}+and+980%3AConferencePaper+not+595%3A%27Not+for+annual+"
        + r"report%27&f=&action_search=Search&c=Published+Articles&c=&sf=author&so=a&rm=&rg=10&sc=1&of=xm",
        "non_journal_proceedings_count": r"search?ln=en&p=affiliation%3ACERN+or+"
        + rf"260%3ACERN+and+260%3A{year}+and+%28980%3ABOOK+or+980%3APROCEEDINGS+or+690%3A%27YELLOW+REPORT%27+"
        + r"or+980%3ABookChapter+or+980%3AREPORT%29+not+595%3A%27Not+for+annual+report%27&action_search="
        + r"Search&op1=a&m1=a&p1=&f1=&c=CERN+Document+Server&sf=&so=d&rm=&rg=10&sc=1&of=xm",
    }
    return endpoint[key]


def set_stat_library_catalog(note, stat, data, date, session):
    hook = HttpHook(
        http_conn_id="library_catalog_conn",
        method="POST",
    )

    endpoint = "api/stats"
    response = hook.run(
        endpoint=endpoint,
        json=data,
        headers={"Authorization": f"Bearer {Variable.get('CATALOG_API_TOKEN')}"},
    )

    records = []
    for _, metric_data in response.json().items():
        for bucket in metric_data["buckets"]:
            records.append(
                LibraryCatalogMetrics(
                    date=date,
                    filter=None,
                    category=endpoint,
                    aggregation=stat,
                    key=bucket["key"],
                    value=int(bucket["count"]),
                    note=note,
                )
            )
    session.add_all(records)


def set_hist_library_catalog(note, endpoint, data, date, filter, session):
    hook = HttpHook(
        http_conn_id="library_catalog_conn",
        method="GET",
    )
    response = hook.run(
        endpoint=f"api/{endpoint}",
        data=data,
        headers={"Authorization": f"Bearer {Variable.get('CATALOG_API_TOKEN')}"},
    )

    records = []

    for bucket in response.json()["buckets"]:
        if "metrics" not in data:
            records.append(
                LibraryCatalogMetrics(
                    date=date,
                    filter=filter,
                    category=endpoint,
                    aggregation=str(bucket["key"]),
                    key="".join(bucket["key"].values()),
                    value=bucket["doc_count"],
                    note=note,
                )
            )
        else:
            for key, value in bucket["metrics"].items():
                if value is None:
                    continue
                records.append(
                    LibraryCatalogMetrics(
                        date=date,
                        filter=filter,
                        category=endpoint,
                        aggregation=str(bucket["key"]),
                        key=key,
                        value=value,
                        note=note,
                    )
                )

    session.add_all(records)
