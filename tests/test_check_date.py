from datetime import date

import pytest

from conftest import REPO_ROOT, FakeDbutils, run_notebook


def test_day_of_month_task_value_matches_today():
    if not (REPO_ROOT / "src/check_date.py").is_file():
        pytest.skip(
            "src/check_date.py deployed as a Databricks Notebook object "
            "(extension stripped); raw-source exec only works against a "
            "plain file checkout, e.g. local pytest or a Git-synced repo."
        )

    dbutils = FakeDbutils()

    run_notebook("src/check_date.py", dbutils)

    expected = date.today().day
    assert dbutils.jobs.taskValues.values["day_of_month"] == expected
    assert dbutils.notebook.exit_value == str(expected)
