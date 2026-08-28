# Databricks notebook source

# Demo ingestion: copy a slice of the sample nyctaxi dataset into our own
# catalog/schema so the training notebook has something writable to read.

# COMMAND ----------

# MAGIC %pip install loguru

# COMMAND ----------

dbutils.library.restartPython()  # noqa: F821

# COMMAND ----------

import sys

from loguru import logger

dbutils.widgets.text("catalog", "ctl_training_dev")  # noqa: F821
dbutils.widgets.text("bundle_root", "")  # noqa: F821

BUNDLE_ROOT = dbutils.widgets.get("bundle_root")  # noqa: F821
if BUNDLE_ROOT and f"{BUNDLE_ROOT}/src" not in sys.path:
    sys.path.append(f"{BUNDLE_ROOT}/src")

from room67.naming import SCHEMA, trips_table  # noqa: E402

catalog = dbutils.widgets.get("catalog")  # noqa: F821
table = trips_table(catalog)

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{SCHEMA}")  # noqa: F821

df = (
    spark.table("samples.nyctaxi.trips")  # noqa: F821
    .select("tpep_pickup_datetime", "tpep_dropoff_datetime", "trip_distance", "fare_amount")
    # dropna before the row cap: room67_trips_raw is what audit_quality's
    # completeness check judges, and downstream tasks rely on that promise
    # (train_demo.py trains on it directly, infer_demo.py scores it as-is).
    .dropna(subset=["trip_distance", "fare_amount"])
    .limit(5000)
)

df.write.mode("overwrite").saveAsTable(table)

# COMMAND ----------

logger.info(f"wrote {df.count()} rows to {table}")

dbutils.notebook.exit("ok")  # noqa: F821
