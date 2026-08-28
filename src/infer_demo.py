# Databricks notebook source

# Demo inference: score the champion model against the raw trips table and
# persist predictions. Runs every day; retraining (see train_demo.py) only
# happens on the 1st of the month.

# COMMAND ----------

# MAGIC %pip install loguru mlflow

# COMMAND ----------

dbutils.library.restartPython()  # noqa: F821

# COMMAND ----------

import sys

import mlflow
from loguru import logger
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "ctl_training_dev")  # noqa: F821
dbutils.widgets.text("bundle_root", "")  # noqa: F821

BUNDLE_ROOT = dbutils.widgets.get("bundle_root")  # noqa: F821
if BUNDLE_ROOT and f"{BUNDLE_ROOT}/src" not in sys.path:
    sys.path.append(f"{BUNDLE_ROOT}/src")

from room67.naming import model_name, predictions_table as predictions_table_name, trips_table  # noqa: E402

catalog = dbutils.widgets.get("catalog")  # noqa: F821
source_table = trips_table(catalog)
predictions_table = predictions_table_name(catalog)
registered_name = model_name(catalog)

# COMMAND ----------

mlflow.set_registry_uri("databricks-uc")

try:
    predict_udf = mlflow.pyfunc.spark_udf(spark, model_uri=f"models:/{registered_name}@champion", result_type="double")  # noqa: F821
except Exception:
    logger.warning(f"no champion version for {registered_name} yet, nothing to score")
    skipped = spark.createDataFrame(  # noqa: F821
        [(None, None, "skipped: no champion model")],
        "predicted_fare_amount double, scored_at timestamp, status string",
    ).withColumn("scored_at", F.current_timestamp())
    skipped.write.mode("append").saveAsTable(predictions_table)
    dbutils.notebook.exit("skipped: no champion model")  # noqa: F821

df = spark.table(source_table).dropna(subset=["trip_distance"])  # noqa: F821

predictions = (
    df.withColumn("predicted_fare_amount", predict_udf(F.col("trip_distance")))
    .withColumn("scored_at", F.current_timestamp())
    .withColumn("status", F.lit("ok"))
)

predictions.write.mode("overwrite").saveAsTable(predictions_table)

# COMMAND ----------

logger.info(f"wrote {predictions.count()} predictions to {predictions_table}")

dbutils.notebook.exit("ok")  # noqa: F821
