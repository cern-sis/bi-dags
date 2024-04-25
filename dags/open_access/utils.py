import datetime
import math
import re

import requests
from common.exceptions import DataFetchError, NotFoundTotalCountOfRecords, WrongInput
from open_access.parsers import get_golden_access_records_ids


def request_again_if_failed(url):
    response = requests.get(url)
    count = 1

    while response.status_code == 502 and count != 10:
        count = count + 1
        response = requests.get(url)
    if response.status_code != 200:
        raise DataFetchError(url=url, status_code=response.status_code)
    return response


def get_total_results_count(data):
    TOTAL_RECORDS_COUNT = re.compile(
        r"Search-Engine-Total-Number-Of-Results" + r":\s(\d*)\s"
    )
    comment_line = data.split("\n")[1]
    match = TOTAL_RECORDS_COUNT.search(comment_line)
    try:
        total_records_count = match.group(1)
        return int(total_records_count)
    except AttributeError:
        raise NotFoundTotalCountOfRecords


def check_year(year):
    current_year = datetime.date.today().year
    if type(year) == int:
        if int(year) >= 2004 and int(year) <= current_year:
            return year
    raise WrongInput(year, current_year)


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
    return records_ids_count


def get_url(query, current_collection="Published+Articles", cds_token=None):
    url = (
        rf"https://cds.cern.ch/search?ln=en&cc={current_collection}&p={query}"
        + r"&action_search=Search&op1=a&m1=a&p1=&f1=&c="
        + r"Published+Articles&c=&sf=&so=d&rm=&rg=100&sc=0&of=xm"
    )
    url = url + (rf"&apikey={cds_token}" if cds_token else "")
    return url
