import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class FakeTaskValues:
    def __init__(self):
        self.values = {}

    def set(self, key, value):
        self.values[key] = value

    def get(self, taskKey, key):
        return self.values[(taskKey, key)]


class FakeJobs:
    def __init__(self, task_values):
        self.taskValues = task_values


class FakeNotebook:
    def __init__(self):
        self.exit_value = None

    def exit(self, value):
        self.exit_value = value
        raise SystemExit(value)


class FakeDbutils(types.SimpleNamespace):
    def __init__(self):
        super().__init__(
            jobs=FakeJobs(FakeTaskValues()),
            notebook=FakeNotebook(),
        )


def run_notebook(relative_path, dbutils):
    source = (REPO_ROOT / relative_path).read_text()
    namespace = {"dbutils": dbutils, "__name__": "__main__"}
    try:
        exec(compile(source, relative_path, "exec"), namespace)
    except SystemExit:
        pass
    return namespace
