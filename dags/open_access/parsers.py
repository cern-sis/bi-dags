import re
import xml.etree.ElementTree as ET
from io import StringIO


def parse_without_names_spaces(xml):
    if type(xml) == str:
        it = ET.iterparse(StringIO(xml))
    else:
        it = ET.iterparse(StringIO(xml.getvalue().decode("utf-8")))
    for _, el in it:
        el.tag = el.tag.rpartition("}")[-1]
    root = it.root
    return root


def is_correct_value(value):
    match value.text.lower():
        case "accepted manuscript":
            return True
        case "preprint":
            return True
        case _:
            return False


def field_has_cc_by(field_value):
    # is CC BY-SA 4.0 falls under the condition of "contains ‘CC-BY’ or ‘CC BY’??
    #
    pattern = re.compile(r"CC(\s|-)?BY(\s|-)?4.0", flags=re.I)
    return bool(pattern.match(field_value))


def is_subset_856_for_green_access(datafields_856):
    at_least_one_found = False
    for datafield in datafields_856:
        subfield = datafield.find("subfield[@code='y']")
        try:
            is_subfield_y_wanted_value = is_correct_value(subfield)
            if not at_least_one_found:
                at_least_one_found = is_subfield_y_wanted_value
            at_least_one_found = is_subfield_y_wanted_value
        except AttributeError:
            pass
    return at_least_one_found


def is_subset_540_preprint_green_access(datafields_540):
    at_least_one_found = False
    for datafield in datafields_540:
        subfield_3 = datafield.find("subfield[@code='3']")
        try:
            is_subfield_3_wanted_value = subfield_3.text.lower() == "preprint"
            if not at_least_one_found:
                at_least_one_found = is_subfield_3_wanted_value
        except AttributeError:
            pass
    return at_least_one_found


def is_subset_540_publication_golden_access(datafields_540):
    at_least_one_found = False
    for datafield in datafields_540:
        subfield_3 = datafield.find("subfield[@code='3']")
        subfield_a = datafield.find("subfield[@code='a']")
        try:
            is_subfield_wanted_3_value = subfield_3.text.lower() == "publication"
            is_subfield_a_wanted_value = field_has_cc_by(subfield_a.text)
            if not at_least_one_found:
                at_least_one_found = bool(
                    is_subfield_wanted_3_value and is_subfield_a_wanted_value
                )
        except AttributeError:
            pass
    return at_least_one_found


def parse_subset_green_access(records):
    filtered_records = []
    for record in records:
        datafields_856 = record.findall("datafield[@tag='856'][@ind1='4'][@ind2=' ']")
        datafields_540 = record.findall("datafield/[@tag='540']")
        if datafields_856 is None:
            continue
        if datafields_540 is None:
            continue
        is_it_wanted_record_by_856 = is_subset_856_for_green_access(datafields_856)
        is_it_wanted_record_by_540_preprint = is_subset_540_preprint_green_access(datafields_540)
        is_it_wanted_record_by_540_publication = not is_subset_540_publication_golden_access(
            datafields_540
        )

        if (
            is_it_wanted_record_by_856
            or is_it_wanted_record_by_540_preprint
            or is_it_wanted_record_by_540_publication
        ):
            filtered_records.append(record)

    return filtered_records


def parse_subset_golden_access(records):
    filtered_records = []
    for record in records:
        datafields_540 = record.findall("datafield/[@tag='540']")
        if datafields_540 is None:
            continue
        is_it_wanted_record_by_540_publication = is_subset_540_publication_golden_access(
            datafields_540
        )

        if is_it_wanted_record_by_540_publication:
            filtered_records.append(record)
    return filtered_records


def get_records_ids(data, record_filter):
    xml = parse_without_names_spaces(data)
    records = xml.findall(".record")
    filtered_records = record_filter(records)
    green_access = []
    for record in filtered_records:
        record_id = record.find("controlfield/[@tag='001']")
        if record_id is not None:
            doi = record_id.text
            green_access.append(doi)
    return green_access


def get_golden_access_records_ids(data):
    return get_records_ids(data, parse_subset_golden_access)


def get_green_access_records_ids(data):
    return get_records_ids(data, parse_subset_green_access)
