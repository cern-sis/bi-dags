import os

import open_access.utils as utils
from common.exceptions import TypeDoesNotExist
from open_access.parsers import get_golden_access_records_ids


class OpenAccessApi:
    query_types = {
        "closed": r"not+540__a:'CC+BY'+not+540__a:'CC-BY'+"
        + r"not+540__f:Bronze+not+540__3:preprint",
        "bronze": r"540__f:'Bronze'",
        "green": r"not+540__a:'CC+BY'+not+540__a:'CC-BY'+not+540__a:"
        + r"'arXiv+nonexclusive-distrib'+not+540__f:'Bronze'",
        "gold": r"540__3:'publication'+and+" + r"(540__a:'CC-BY'+OR++540__a:'CC+BY')",
    }

    def __init__(self, year, cds_token=None):
        self.base_query = (
            r"(affiliation:CERN+or+595:'For+annual+report')"
            + rf"and+year:{year}+not+980:ConferencePaper+"
            + r"not+980:BookChapter"
        )
        self.cds_token = cds_token or os.environ.get("CDS_TOKEN")

    def _get_url(self, query, current_collection="Published+Articles"):
        url = (
            rf"https://cds.cern.ch/search?ln=en&cc={current_collection}&p={query}"
            + r"&action_search=Search&op1=a&m1=a&p1=&f1=&c="
            + r"Published+Articles&c=&sf=&so=d&rm=&rg=100&sc=0&of=xm"
            + rf"&apikey={self.cds_token}"
            if self.cds_token
            else ""
        )
        return url

    def _get_records_count(self, query_type):
        if query_type not in self.query_types:
            raise TypeDoesNotExist
        self.url = self._get_url(f"{self.base_query}+{self.query_types[query_type]}")
        response = utils.request_again_if_failed(self.url)
        total = utils.get_total_results_count(response.text)
        return int(total)

    def get_closed_access_total_count(self):
        return self._get_records_count("closed")

    def get_bronze_access_total_count(self):
        return self._get_records_count("bronze")

    def get_green_access_total_count(self):
        total = self._get_records_count("green")
        total_gold_access_records_inside_of_green = utils.filter_records(
            total=total, url=self.url, filter_func=get_golden_access_records_ids
        )
        return total - total_gold_access_records_inside_of_green

    def get_gold_access_total_count(self):
        total = self._get_records_count("gold")
        total_only_gold_access_records = utils.filter_records(
            total=total, url=self.url, filter_func=get_golden_access_records_ids
        )
        return total_only_gold_access_records
