# Databricks notebook source

# Demo training: fit a trivial linear model (fare_amount ~ trip_distance) on
# the raw table the ingest task wrote. Not production ML, just a smoke test
# that a downstream task can read the ingested data.

# COMMAND ----------

# MAGIC %pip install loguru scikit-learn mlflow

# COMMAND ----------

dbutils.library.restartPython()  # noqa: F821

# COMMAND ----------

from loguru import logger

dbutils.widgets.text("catalog", "ctl_training_dev")  # noqa: F821
catalog = dbutils.widgets.get("catalog")  # noqa: F821

schema = "m3"
table = f"{catalog}.{schema}.namaew_trips_raw"

# COMMAND ----------

import mlflow
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

pdf = spark.table(table).dropna(subset=["trip_distance", "fare_amount"]).toPandas()  # noqa: F821

train_df, test_df = train_test_split(pdf, test_size=0.2, random_state=42)

lr = LinearRegression()
model = lr.fit(train_df[["trip_distance"]], train_df["fare_amount"])

predictions = model.predict(test_df[["trip_distance"]])
rmse = mean_squared_error(test_df["fare_amount"], predictions) ** 0.5

# COMMAND ----------

mlflow.set_registry_uri("databricks-uc")
model_name = f"{catalog}.{schema}.namaew_fare_model"

with mlflow.start_run():
    mlflow.log_metric("rmse", rmse)
    info = mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name=model_name,
        input_example=train_df[["trip_distance"]].head(),
    )

model_version = info.registered_model_version

# COMMAND ----------

logger.info(f"rows trained on: {len(train_df)}")
logger.info(f"rmse: {rmse:.2f}")
logger.info(f"registered {model_name} version {model_version}")

dbutils.jobs.taskValues.set(key="rmse", value=rmse)  # noqa: F821
dbutils.jobs.taskValues.set(key="model_version", value=model_version)  # noqa: F821

dbutils.notebook.exit("ok")  # noqa: F821
