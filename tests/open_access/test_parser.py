from open_access.parsers import (
    get_golden_access_records_ids,
    get_green_access_records_ids,
    is_subset_540_preprint_green_access,
    is_subset_540_publication_golden_access,
    is_subset_856_for_green_access,
    parse_without_names_spaces,
)

expected_golden = [
    "2894668",
    "2891488",
    "2888511",
    "2888151",
    "2884471",
    "2884470",
    "2883672",
    "2882429",
    "2882335",
    "2882328",
    "2882327",
    "2882324",
    "2882322",
    "2882311",
    "2882298",
]

expected_green = [
    "2894668",
    "2891489",
    "2891488",
    "2891487",
    "2888511",
    "2888151",
    "2886038",
    "2884472",
    "2884471",
    "2884470",
    "2884469",
    "2883672",
    "2882429",
    "2882335",
    "2882328",
    "2882327",
    "2882324",
    "2882322",
    "2882311",
    "2882298",
]


def test_get_golden_access_records_dois(shared_datadir):
    with open(shared_datadir / "search.xml") as file:
        records_ids = get_golden_access_records_ids(file.read())
        assert records_ids == expected_golden


def test_parse_subset_856(shared_datadir):
    with open(shared_datadir / "search.xml") as file:
        filtered_records_count = 0
        parsed_records = parse_without_names_spaces(file.read())
        records = parsed_records.findall(".record")
        for record in records:
            datafields_856 = record.findall(
                "datafield[@tag='856'][@ind1='4'][@ind2=' ']"
            )
            is_it_wanted_record_by_856 = is_subset_856_for_green_access(datafields_856)
            if is_it_wanted_record_by_856:
                filtered_records_count = filtered_records_count + 1
        assert filtered_records_count == 0


def test_parse_subset_540_preprint(shared_datadir):
    with open(shared_datadir / "search.xml") as file:
        filtered_records_count = 0
        parsed_records = parse_without_names_spaces(file.read())
        records = parsed_records.findall(".record")
        for record in records:
            datafields_540 = record.findall(
                "datafield[@tag='540'][@ind1=' '][@ind2=' ']"
            )
            is_it_wanted_record_by_540 = is_subset_540_preprint_green_access(
                datafields_540
            )
            if is_it_wanted_record_by_540:
                filtered_records_count = filtered_records_count + 1
        assert filtered_records_count == 20


def test_parse_subset_540_publications(shared_datadir):
    with open(shared_datadir / "search.xml") as file:
        filtered_records_count = 0
        parsed_records = parse_without_names_spaces(file.read())
        records = parsed_records.findall(".record")
        for record in records:
            datafields_540 = record.findall(
                "datafield[@tag='540'][@ind1=' '][@ind2=' ']"
            )
            is_it_wanted_record_by_540 = is_subset_540_publication_golden_access(
                datafields_540
            )
            if is_it_wanted_record_by_540:
                filtered_records_count = filtered_records_count + 1
        assert filtered_records_count == 15


def test_get_green_access_records_dois(shared_datadir):
    with open(shared_datadir / "search.xml") as file:
        records_ids = get_green_access_records_ids(file.read())
        assert records_ids == expected_green
