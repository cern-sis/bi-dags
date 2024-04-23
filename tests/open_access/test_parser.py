from open_access.parsers import get_golden_access_records_ids

expected = [
    "2891488",
    "2888511",
    "2884471",
    "2884470",
    "2883672",
    "2882429",
    "2882335",
    "2882324",
    "2882311",
]


def test_get_golden_access_records_dois(shared_datadir):
    with open(shared_datadir / "search.xml") as file:
        records_ids = get_golden_access_records_ids(file.read())
        assert records_ids == expected
