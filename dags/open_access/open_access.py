from functools import reduce

import open_access.utils as utils
import pendulum
from airflow.decorators import dag, task


@dag(
    start_date=pendulum.today("UTC").add(days=-1),
    schedule="@monthly",
    params={"year": 2023},
)
def oa_dag():
    @task()
    def fetch_data_task(query, **kwargs):
        year = kwargs["params"].get("year")
        base_query = (
            r"(affiliation:CERN+or+595:'For+annual+report')"
            + rf"and+year:{year}+not+980:ConferencePaper+"
            + r"not+980:BookChapter"
        )
        type_of_query = [*query][0]
        url = utils.get_url(f"{base_query}+{query[type_of_query]}")
        data = utils.get_data(url)
        total = utils.get_total_results_count(data.text)
        return {type_of_query: total}

    @task()
    def join(values):
        return reduce(lambda a, b: {**a, **b}, values)

    results = fetch_data_task.expand(
        query=[
            {"closed": utils.closed_access_query},
            {"bronze": utils.bronze_access_query},
            {"green": utils.green_access_query},
            {"gold": utils.gold_access_query},
        ],
    )
    join(results)


OA_dag = oa_dag()
