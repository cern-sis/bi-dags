from open_access.parsers import get_golden_access_records_ids

expected = [
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


def test_get_golden_access_records_dois(shared_datadir):
    with open(shared_datadir / "search.xml") as file:
        records_ids = get_golden_access_records_ids(file.read())
        assert records_ids == expected
