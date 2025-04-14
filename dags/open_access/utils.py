import logging
import math

from airflow.exceptions import AirflowException
from airflow.providers.http.hooks.http import HttpHook
from common.utils import get_total_results_count
from open_access.parsers import (
    get_golden_access_records_ids,
    get_green_access_records_ids,
)
from tenacity import retry_if_exception_type, stop_after_attempt


def get_count_http_hook(total, url, record_extractor):
    http_hook = HttpHook(http_conn_id="cds", method="GET")
    iterations = math.ceil(total / 100.0)
    records_ids_count = 0
    all_ids = []
    for i in range(0, iterations):
        jrec = (i * 100) + 1
        full_url = f"{url}&jrec={jrec}"
        response = http_hook.run_with_advanced_retry(
            endpoint=full_url,
            _retry_args={
                "stop": stop_after_attempt(3),
                "retry": retry_if_exception_type(AirflowException),
            },
        )
        all_ids.extend(record_extractor(response.text))
        records_ids_count = records_ids_count + len(record_extractor(response.text))
    logging.info(f"In total was found {records_ids_count} records")
    logging.info(f"Records ids: {all_ids}")
    return records_ids_count


def get_golden_access_count(total, url):
    return get_count_http_hook(total, url, get_golden_access_records_ids)


def get_green_access_count(total, url):
    return get_count_http_hook(total, url, get_green_access_records_ids)


def get_url(query, current_collection="Published+Articles"):
    url = (
        rf"https://cds.cern.ch/search?ln=en&cc={current_collection}&p={query}"
        + r"&action_search=Search&op1=a&m1=a&p1=&f1=&c="
        + r"Published+Articles&c=&sf=&so=d&rm=&rg=1&sc=0&of=xm"
    )
    return url


def fetch_count_from_comments(endpoint):
    http_hook = HttpHook(http_conn_id="cds", method="GET")
    response = http_hook.run_with_advanced_retry(
        endpoint=endpoint,
        _retry_args={
            "stop": stop_after_attempt(3),
            "retry": retry_if_exception_type(AirflowException),
        },
    )
    count = get_total_results_count(response.text)
    return count


def fetch_count_from_parsed_records(
    parameters,
    count_function,
    previous={},
):
    http_hook = HttpHook(http_conn_id="cds", method="GET")
    response = http_hook.run_with_advanced_retry(
        endpoint=parameters["endpoint"],
        _retry_args={
            "stop": stop_after_attempt(3),
            "retry": retry_if_exception_type(AirflowException),
        },
    )
    endpoint = parameters["endpoint"]
    total = get_total_results_count(response.text)
    count = count_function(total, endpoint)
    previous.update({parameters["type_of_query"]: count})
    return previous


def generate_params(query_object, year):
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
