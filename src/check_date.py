# Databricks notebook source

# Gate: retrain (ingest+train+validate) only runs on the 1st of the month.
# Other days just run inference against the current champion model.
# Cluster/job schedule run in UTC, so this compares day-of-month in UTC too.

# COMMAND ----------

from datetime import date

day_of_month = date.today().day

dbutils.jobs.taskValues.set(key="day_of_month", value=day_of_month)  # noqa: F821

# COMMAND ----------

dbutils.notebook.exit(str(day_of_month))  # noqa: F821
