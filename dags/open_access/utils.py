import datetime
import math
import re

import backoff
import requests
from common.exceptions import WrongInput
from open_access.parsers import get_golden_access_records_ids


def get_url(query, current_collection="Published+Articles"):
    url = (
        rf"https://cds.cern.ch/search?ln=en&cc={current_collection}&p={query}"
        + r"&action_search=Search&op1=a&m1=a&p1=&f1=&c="
        + r"Published+Articles&c=&sf=&so=d&rm=&rg=100&sc=0&of=xm"
    )
    return url


def get_gold_access_count(total, url):
    iterations = math.ceil(total / 100.0)
    golden_access_records_ids_count = 0

    for i in range(0, iterations):
        jrec = (i * 100) + 1
        full_url = f"{url}&jrec={jrec}"
        data = get_data(full_url)
        golden_access_records_ids_count = golden_access_records_ids_count + len(
            get_golden_access_records_ids(data.text)
        )
    return golden_access_records_ids_count


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
        return 0


closed_access_query = (
    r"not+540__a:'CC+BY'+not+540__a:'CC-BY'+" + r"not+540__f:Bronze+not+540__3:preprint"
)
bronze_access_query = r"540__f:'Bronze'"
green_access_query = (
    r"not+540__a:'CC+BY'+not+540__a:'CC-BY'+not+540__a:"
    + r"'arXiv+nonexclusive-distrib'+not+540__f:'Bronze'"
)
gold_access_query = (
    r"540__3:'publication'+and+" + r"(540__a:'CC-BY'+OR++540__a:'CC+BY')"
)

cern_read_and_publish = r"540__f:'CERN-RP"
cern_individual_apcs = r"540__f:'CERN-APC'"
scoap3 = r"540__f:'SCOAP3'"
other = r"540__f:'Other'"
other_collective_models = r"540__f:'Collective'"


@backoff.on_exception(
    backoff.expo, requests.exceptions.ProxyError, max_time=1000, max_tries=10
)
def get_data(url):
    return requests.get(url)


def check_year(year):
    current_year = datetime.date.today().year
    if type(year) == int:
        if int(year) >= 2004 and int(year) <= current_year:
            return year
    raise WrongInput(year, current_year)
