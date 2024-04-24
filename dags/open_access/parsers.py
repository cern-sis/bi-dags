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


def get_golden_access_records_ids(data):
    xml = parse_without_names_spaces(data)
    records = xml.findall(".record")
    golden_access = []
    for record in records:
        datafields = record.findall("datafield/[@tag='540']")
        if datafields is None:
            continue
        for datafield in datafields:
            record_type = datafield.find("subfield/[@code='3']")
            license = datafield.find("subfield/[@code='a']")
            if record_type is not None and license is not None:
                if (
                    "CC" in license.text
                    and "BY" in license.text
                    and record_type.text == "publication"
                ):
                    record_id = record.find("controlfield/[@tag='001']")
                    if record_id is not None:
                        doi = record_id.text
                        golden_access.append(doi)
    return golden_access
