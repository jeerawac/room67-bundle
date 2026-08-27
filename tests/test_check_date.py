from datetime import date

from conftest import FakeDbutils, run_notebook


def test_day_of_month_task_value_matches_today():
    dbutils = FakeDbutils()

    run_notebook("src/check_date.py", dbutils)

    expected = date.today().day
    assert dbutils.jobs.taskValues.values["day_of_month"] == expected
    assert dbutils.notebook.exit_value == str(expected)
