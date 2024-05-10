import datetime
import re

import requests
from common.exceptions import DataFetchError, NotFoundTotalCountOfRecords, WrongInput


def request_again_if_failed(url, cds_token=None):
    if cds_token:
        header = {"Authorization": f"token {cds_token}"}
        response = requests.get(url, header)
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
