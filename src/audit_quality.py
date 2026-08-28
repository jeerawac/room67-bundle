# Databricks notebook source
# MAGIC %md
# MAGIC # Data-quality audit — against the table `ingest` just wrote
# MAGIC
# MAGIC The expectations in `namaew/checks.py` are proved against fixtures by
# MAGIC `tests/test_checks.py` on the runner. This task runs the same functions
# MAGIC against the table the ingest task just wrote, which is the only place the
# MAGIC quality of this month's data can be established.
# MAGIC
# MAGIC The task FAILS on any violation, so `train` never runs against data that
# MAGIC has already been rejected (Write-Audit-Publish).

# COMMAND ----------

import json
import sys

dbutils.widgets.text("catalog", "ctl_training_dev")  # noqa: F821
dbutils.widgets.text("bundle_root", "")  # noqa: F821

BUNDLE_ROOT = dbutils.widgets.get("bundle_root")  # noqa: F821
if BUNDLE_ROOT and f"{BUNDLE_ROOT}/src" not in sys.path:
    sys.path.append(f"{BUNDLE_ROOT}/src")

from namaew.checks import audit  # noqa: E402
from namaew.naming import trips_table  # noqa: E402

catalog = dbutils.widgets.get("catalog")  # noqa: F821
TABLE = trips_table(catalog)

# COMMAND ----------

violations = audit(spark.table(TABLE))  # noqa: F821
payload = {"table": TABLE, "level": "data quality", "violations": violations}
print(json.dumps(payload, indent=2))

if violations:
    raise AssertionError(f"{len(violations)} data-quality violation(s): {violations}")

dbutils.notebook.exit(json.dumps(payload))  # noqa: F821
