from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_CONFIG = yaml.safe_load((REPO_ROOT / "databricks.yml").read_text())

# databricks.yml declares `include: resources/*.yml`, which the Databricks CLI
# resolves at deploy/validate time. Plain yaml.safe_load doesn't follow that,
# so merge the included files here too, tracking each job's source directory
# to resolve its (file-relative) notebook paths correctly below.
JOBS = {}
for job_key, job in BUNDLE_CONFIG.get("resources", {}).get("jobs", {}).items():
    JOBS[job_key] = (job, REPO_ROOT)
for resource_file in sorted((REPO_ROOT / "resources").glob("*.yml")):
    config = yaml.safe_load(resource_file.read_text())
    for job_key, job in config.get("resources", {}).get("jobs", {}).items():
        JOBS[job_key] = (job, resource_file.parent)


def all_jobs():
    return [(job_key, job) for job_key, (job, _) in JOBS.items()]


@pytest.mark.parametrize("job_key,job", all_jobs())
def test_notebook_paths_exist_on_disk(job_key, job):
    base_dir = JOBS[job_key][1]
    for task in job["tasks"]:
        notebook_task = task.get("notebook_task")
        if notebook_task is None:
            continue
        notebook_path = (base_dir / notebook_task["notebook_path"]).resolve()
        # Deployed as a Databricks job, notebook-source .py files are imported as
        # Notebook objects with the extension stripped, so check both forms.
        exists = notebook_path.is_file() or notebook_path.with_suffix("").is_file()
        assert exists, f"{job_key}/{task['task_key']}: missing {notebook_path}"


@pytest.mark.parametrize("job_key,job", all_jobs())
def test_depends_on_task_keys_exist_in_same_job(job_key, job):
    task_keys = {task["task_key"] for task in job["tasks"]}
    for task in job["tasks"]:
        for dep in task.get("depends_on", []):
            assert dep["task_key"] in task_keys, (
                f"{job_key}/{task['task_key']}: depends_on unknown task_key {dep['task_key']!r}"
            )


def test_gate_retrain_has_both_true_and_false_consumers():
    job = JOBS["namaew"][0]
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
