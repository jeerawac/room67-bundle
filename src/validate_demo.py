# Databricks notebook source

# Gate: fail if the freshly trained model's RMSE is above threshold. On
# pass, tag the model version as "champion" so the inference notebook
# picks it up. The comparison itself lives in namaew/gate.py.

# COMMAND ----------

# MAGIC %pip install loguru mlflow

# COMMAND ----------

dbutils.library.restartPython()  # noqa: F821

# COMMAND ----------

import sys

dbutils.widgets.text("catalog", "ctl_training_dev")  # noqa: F821
dbutils.widgets.text("rmse_threshold", "5.0")  # noqa: F821
dbutils.widgets.text("bundle_root", "")  # noqa: F821

BUNDLE_ROOT = dbutils.widgets.get("bundle_root")  # noqa: F821
if BUNDLE_ROOT and f"{BUNDLE_ROOT}/src" not in sys.path:
    sys.path.append(f"{BUNDLE_ROOT}/src")

from namaew.gate import exceeds_threshold  # noqa: E402
from namaew.naming import model_name  # noqa: E402

catalog = dbutils.widgets.get("catalog")  # noqa: F821
rmse_threshold = float(dbutils.widgets.get("rmse_threshold"))  # noqa: F821
registered_name = model_name(catalog)

# COMMAND ----------

import mlflow
from loguru import logger
from mlflow.tracking import MlflowClient

rmse = float(dbutils.jobs.taskValues.get(taskKey="train", key="rmse"))  # noqa: F821
model_version = dbutils.jobs.taskValues.get(taskKey="train", key="model_version")  # noqa: F821

logger.info(f"model version {model_version} rmse: {rmse:.2f} (threshold: {rmse_threshold:.2f})")

if exceeds_threshold(rmse, rmse_threshold):
    raise ValueError(
        f"rmse {rmse:.2f} exceeds threshold {rmse_threshold:.2f}, "
        f"refusing to promote model version {model_version}"
    )

# COMMAND ----------

mlflow.set_registry_uri("databricks-uc")
MlflowClient().set_registered_model_alias(registered_name, "champion", model_version)

logger.info(f"promoted {registered_name} version {model_version} to champion")

dbutils.notebook.exit("ok")  # noqa: F821
