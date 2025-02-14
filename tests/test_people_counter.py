import pytest
from airflow.models import DagBag
from airflow.utils.context import Context
from freezegun import freeze_time

dagbag = DagBag()


@freeze_time("2024-12-11")
class TestPeopleCounter:
    dag = dagbag.get_dag("library_people_counter_dag")
    context = {"ds": "2024-12-11", "ds_nodash": "20241211"}

    def test_set_params(self):
        task = self.dag.get_task("set_params")

        res = task.execute(context=Context(self.context))
        assert res == {
            "start": "20241211",
            "end": "20241212",
            "resolution": "hour",
        }

    @pytest.mark.vcr
    def test_fetch_occupancy(self):
        task = self.dag.get_task("fetch_occupancy")
        task.op_args = (
            {
                "start": "20241211",
                "end": "20241212",
                "resolution": "hour",
            },
        )
        res = task.execute(context=Context())
        assert res["data"][0]["start"] == "2024-12-11 00:00:00"
        assert res["data"][23]["end"] == "2024-12-12 00:00:00"

    @pytest.mark.vcr
    def test_fetch_inout(self):
        task = self.dag.get_task("fetch_inout")
        task.op_args = (
            {
                "start": "20241211",
                "end": "20241212",
                "resolution": "hour",
            },
        )
        res = task.execute(context=Context())
        assert res["data"][0]["start"] == "2024-12-11 00:00:00"
        assert res["data"][23]["end"] == "2024-12-12 00:00:00"
