# Databricks notebook source

# CI entrypoint: runs the repo's pytest suite on a job cluster so
# databricks.yml wiring and pure-python notebook logic get checked
# without needing a local Databricks Connect setup.

# COMMAND ----------

# MAGIC %pip install pytest pyyaml

# COMMAND ----------

dbutils.library.restartPython()  # noqa: F821

# COMMAND ----------

import sys

sys.dont_write_bytecode = True

import pytest

dbutils.widgets.text("repo_root", "")  # noqa: F821
repo_root = dbutils.widgets.get("repo_root")  # noqa: F821

sys.path.insert(0, repo_root)

exit_code = pytest.main(["-p", "no:cacheprovider", "-v", f"{repo_root}/tests"])

# COMMAND ----------

dbutils.notebook.exit("ok" if exit_code == 0 else f"failed: exit code {exit_code}")  # noqa: F821
