import logging
import math

from common.utils import request_again_if_failed
from open_access.parsers import get_golden_access_records_ids


def get_gold_access_count(total, url):
    iterations = math.ceil(total / 100.0)
    records_ids_count = 0
    for i in range(0, iterations):
        jrec = (i * 100) + 1
        full_url = f"{url}&jrec={jrec}"
        response = request_again_if_failed(full_url)
        records_ids_count = records_ids_count + len(
            get_golden_access_records_ids(response.text)
        )
    logging.info(f"In total was found {records_ids_count} golden access records")
    return records_ids_count


def get_url(query, current_collection="Published+Articles"):
    url = (
        rf"https://cds.cern.ch/search?ln=en&cc={current_collection}&p={query}"
        + r"&action_search=Search&op1=a&m1=a&p1=&f1=&c="
        + r"Published+Articles&c=&sf=&so=d&rm=&rg=100&sc=0&of=xm"
    )
    return url
