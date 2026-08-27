# Databricks notebook source

# Demo inference: score the champion model against the raw trips table and
# persist predictions. Runs every day; retraining (see train_demo.py) only
# happens on the 1st of the month.

# COMMAND ----------

# MAGIC %pip install loguru mlflow

# COMMAND ----------

dbutils.library.restartPython()  # noqa: F821

# COMMAND ----------

import mlflow
from loguru import logger
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "ctl_training_dev")  # noqa: F821
catalog = dbutils.widgets.get("catalog")  # noqa: F821

schema = "m3"
source_table = f"{catalog}.{schema}.namaew_trips_raw"
predictions_table = f"{catalog}.{schema}.namaew_predictions"
model_name = f"{catalog}.{schema}.namaew_fare_model"

# COMMAND ----------

mlflow.set_registry_uri("databricks-uc")

try:
    predict_udf = mlflow.pyfunc.spark_udf(spark, model_uri=f"models:/{model_name}@champion", result_type="double")  # noqa: F821
except Exception:
    logger.warning(f"no champion version for {model_name} yet, nothing to score")
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
