# Databricks notebook source

# Demo training: fit a trivial linear model (fare_amount ~ trip_distance) on
# the table the ingest+audit tasks already vouched for. Not production ML,
# just a smoke test that a downstream task can read the ingested data. The
# fit/eval logic lives in room67/model.py, unit-tested without Spark.

# COMMAND ----------

# MAGIC %pip install loguru scikit-learn mlflow

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

from room67.naming import model_name, trips_table  # noqa: E402

catalog = dbutils.widgets.get("catalog")  # noqa: F821
table = trips_table(catalog)

# COMMAND ----------

import mlflow

from room67.model import fit_and_evaluate

pdf = spark.table(table).dropna(subset=["trip_distance", "fare_amount"]).toPandas()  # noqa: F821

model, rmse, train_df = fit_and_evaluate(pdf)

# COMMAND ----------

mlflow.set_registry_uri("databricks-uc")
registered_name = model_name(catalog)

with mlflow.start_run():
    mlflow.log_metric("rmse", rmse)
    info = mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name=registered_name,
        input_example=train_df[["trip_distance"]].head(),
    )

model_version = info.registered_model_version

# COMMAND ----------

logger.info(f"rows trained on: {len(train_df)}")
logger.info(f"rmse: {rmse:.2f}")
logger.info(f"registered {registered_name} version {model_version}")

dbutils.jobs.taskValues.set(key="rmse", value=rmse)  # noqa: F821
dbutils.jobs.taskValues.set(key="model_version", value=model_version)  # noqa: F821

dbutils.notebook.exit("ok")  # noqa: F821
