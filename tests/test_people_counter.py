import pytest
from airflow.models import DagBag
from airflow.utils.context import Context
from freezegun import freeze_time

dagbag = DagBag()


@freeze_time("2024-12-11")
class TestPeopleCounter:
    dag = dagbag.get_dag("library_people_counter_dag")

    @pytest.mark.vcr
    def test_fetch_occupancy(self):
        task = self.dag.get_task("fetch_occupancy")
        res = task.execute(
            context=Context({"ds": "2024-12-11", "ds_nodash": "20241211"})
        )
        assert res["data"][0]["start"] == "2024-12-11 00:00:00"
        assert res["data"][23]["end"] == "2024-12-12 00:00:00"
