from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_CONFIG = yaml.safe_load((REPO_ROOT / "databricks.yml").read_text())


def all_jobs():
    return BUNDLE_CONFIG["resources"]["jobs"].items()


@pytest.mark.parametrize("job_key,job", all_jobs())
def test_notebook_paths_exist_on_disk(job_key, job):
    for task in job["tasks"]:
        notebook_task = task.get("notebook_task")
        if notebook_task is None:
            continue
        notebook_path = (REPO_ROOT / notebook_task["notebook_path"]).resolve()
        assert notebook_path.is_file(), f"{job_key}/{task['task_key']}: missing {notebook_path}"


@pytest.mark.parametrize("job_key,job", all_jobs())
def test_depends_on_task_keys_exist_in_same_job(job_key, job):
    task_keys = {task["task_key"] for task in job["tasks"]}
    for task in job["tasks"]:
        for dep in task.get("depends_on", []):
            assert dep["task_key"] in task_keys, (
                f"{job_key}/{task['task_key']}: depends_on unknown task_key {dep['task_key']!r}"
            )


def test_gate_retrain_has_both_true_and_false_consumers():
    job = BUNDLE_CONFIG["resources"]["jobs"]["namaew_job"]
    outcomes = {
        dep.get("outcome")
        for task in job["tasks"]
        for dep in task.get("depends_on", [])
        if dep["task_key"] == "gate_retrain"
    }
    assert outcomes == {"true", "false"}


def test_rmse_threshold_default_parses_as_float():
    default = BUNDLE_CONFIG["variables"]["rmse_threshold"]["default"]
    float(default)
