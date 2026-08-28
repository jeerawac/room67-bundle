# Databricks notebook source

# Gate: retrain (ingest+train+validate) only runs on the 1st of the month.
# Other days just run inference against the current champion model.
# Cluster/job schedule run in UTC, so this compares day-of-month in UTC too.
# The rule itself lives in room67/dates.py; this notebook is the shell that
# reads it and reports it to the job.

# COMMAND ----------

import sys
from datetime import date

dbutils.widgets.text("bundle_root", "")  # noqa: F821

BUNDLE_ROOT = dbutils.widgets.get("bundle_root")  # noqa: F821
if BUNDLE_ROOT and f"{BUNDLE_ROOT}/src" not in sys.path:
    sys.path.append(f"{BUNDLE_ROOT}/src")

from room67.dates import day_of_month  # noqa: E402

result = day_of_month(date.today())

dbutils.jobs.taskValues.set(key="day_of_month", value=result)  # noqa: F821

# COMMAND ----------

dbutils.notebook.exit(str(result))  # noqa: F821
