import datetime
import re

from common.exceptions import NotFoundTotalCountOfRecords, WrongInput


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
