import re

import backoff
import requests


def get_url(query, current_collection="Published+Articles"):
    url = f"https://cds.cern.ch/search?ln=en&cc={current_collection}&p={query}\
    &action_search=Search&op1=a&m1=a&p1=&f1=&c=\
    Published+Articles&c=&sf=&so=d&rm=&rg=100&sc=0&of=xm"
    return url


def get_total_results_count(data):
    TOTAL_RECORDS_COUNT = re.compile(
        r"Search-Engine-Total-Number-Of-Results\
        :\s(\d*)\s"
    )
    comment_line = data.split("\n")[1]
    match = TOTAL_RECORDS_COUNT.search(comment_line)
    try:
        total_records_count = match.group(1)
        return total_records_count
    except AttributeError:
        return 0


closed_access_query = "not+540__a:'CC+BY'+not+540__a:'CC-BY'+\
            not+540__f:Bronze+not+540__3:preprint"
bronze_access_query = "540__f:'Bronze'"
green_access_query = "not+540__a:'CC+BY'+not+540__a:'CC-BY'+not+540__a:\
        'arXiv+nonexclusive-distrib'+not+540__f:'Bronze'"
gold_access_query = "540__3:'publication'+and+\
        (540__a:'CC-BY'+OR++540__a:'CC+BY')"


@backoff.on_exception(
    backoff.expo, requests.exceptions.ProxyError, max_time=120, max_tries=5
)
def get_data(url):
    return requests.get(url)
