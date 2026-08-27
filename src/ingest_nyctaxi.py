# Databricks notebook source

# Demo ingestion: copy a slice of the sample nyctaxi dataset into our own
# catalog/schema so the training notebook has something writable to read.

# COMMAND ----------

# MAGIC %pip install loguru

# COMMAND ----------

dbutils.library.restartPython()  # noqa: F821

# COMMAND ----------

from loguru import logger

dbutils.widgets.text("catalog", "ctl_training_dev")  # noqa: F821
catalog = dbutils.widgets.get("catalog")  # noqa: F821

schema = "m3"
table = f"{catalog}.{schema}.namaew_trips_raw"

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")  # noqa: F821

df = (
    spark.table("samples.nyctaxi.trips")  # noqa: F821
    .select("tpep_pickup_datetime", "tpep_dropoff_datetime", "trip_distance", "fare_amount")
    .limit(5000)
)

df.write.mode("overwrite").saveAsTable(table)

# COMMAND ----------

logger.info(f"wrote {df.count()} rows to {table}")

dbutils.notebook.exit("ok")  # noqa: F821
