import os
import xml.etree.ElementTree as ET

from common.exceptions import VariableValueIsMissing

from .constants import ONLY_CERN_SUBJECTS


def get_endpoint(key, year):
    cds_token = os.environ.get("CDS_TOKEN", "")
    if cds_token:
        base = f"tools/custom_query_summary.py?start={year}&end={year}&apikey={cds_token}&refresh=1&repeated_values=0"
        endpoints = {"publications": base, "subjects": base + "&otag=65017a"}
        return endpoints[key]
    raise VariableValueIsMissing("CDS_TOKEN")


def get_publications_by_year(content):
    root = ET.fromstring(content)
    yearly_report = root.find("yearly_report")
    publication_report_count = yearly_report.attrib
    del publication_report_count["year"]
    journals = {}
    for journal in yearly_report.findall("line"):
        name = journal.find("result").text
        if "TOTAL" in name:
            continue
        journals[name] = journal.find("nb").text
    return publication_report_count, journals


def get_subjects_by_year(content):
    root = ET.fromstring(content)
    yearly_report = root.find("yearly_report")
    subjects = {}
    for subject in yearly_report.findall("line"):
        name = subject.find("result").text
        if "TOTAL" in name or name not in ONLY_CERN_SUBJECTS:
            continue
        subjects[name] = subject.find("nb").text
    return subjects
