from example_dag.example_dag import fetch, pull


def test_test_dag_fetch():
    assert fetch() == "Test String"


def test_test_dag_pull():
    assert pull("Test String") == "Test String"
