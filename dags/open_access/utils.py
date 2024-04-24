import datetime
import math
import re

import requests
from common.exceptions import DataFetchError, NotFoundTotalCountOfRecords, WrongInput


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


cern_read_and_publish = r"540__f:'CERN-RP"
cern_individual_apcs = r"540__f:'CERN-APC'"
scoap3 = r"540__f:'SCOAP3'"
other = r"540__f:'Other'"
other_collective_models = r"540__f:'Collective'"


def check_year(year):
    current_year = datetime.date.today().year
    if type(year) == int:
        if int(year) >= 2004 and int(year) <= current_year:
            return year
    raise WrongInput(year, current_year)


def filter_records(total, url, filter_func):
    iterations = math.ceil(total / 100.0)
    records_ids_count = 0
    for i in range(0, iterations):
        jrec = (i * 100) + 1
        full_url = f"{url}&jrec={jrec}"
        response = request_again_if_failed(full_url)
        records_ids_count = records_ids_count + len(filter_func(response.text))
    return records_ids_count
