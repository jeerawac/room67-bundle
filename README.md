# room67-bundle

Databricks Asset Bundle demo: monthly retrain + daily inference pipeline on the NYC taxi sample dataset, gated by RMSE.

## Pipeline

Job `room67` runs daily (`0 0 2 * * ?` UTC):

1. **check_date** — reads day of month, sets task value.
2. **gate_retrain** — condition task, true only on the 1st.
3. If retrain gate true: **ingest** → **data_quality** → **train** → **validate** (Write-Audit-Publish: each of the last two fails the run rather than letting a bad table or a bad model flow downstream)
   - `ingest_nyctaxi.py`: copies a 5000-row slice of `samples.nyctaxi.trips` into `{catalog}.m3.room67_trips_raw`.
   - `audit_quality.py`: fails the run if the table just written has nulls, negative values, or is empty.
   - `train_demo.py`: fits `LinearRegression` (fare_amount ~ trip_distance), logs run + registers model to Unity Catalog as `{catalog}.m3.room67_fare_model`.
   - `validate_demo.py`: fails the run if RMSE > `rmse_threshold`; otherwise aliases the new version `champion`.
4. **infer** — runs `run_if: ALL_DONE` after gate/validate; scores current `champion` model against raw table, writes to `{catalog}.m3.room67_predictions`. Skips gracefully (writes a `status="skipped"` row) if no champion exists yet.

The notebooks in `src/` are thin: widgets in, `spark`/`mlflow` calls out. The actual rules — date math, table/model naming, the RMSE gate, the data-quality expectations, the model fit/eval — live in the importable package `src/room67/`, which is what `tests/` exercises directly.

## Repo layout

```
databricks.yml            bundle config, includes resources/*.yml
resources/
  room67.job.yml           the pipeline job
src/
  check_date.py            gate: day-of-month check
  ingest_nyctaxi.py        ingest sample data
  audit_quality.py         data-quality gate on the ingested table
  train_demo.py            train + register model
  validate_demo.py         RMSE gate + promote to champion
  infer_demo.py            score champion model
  room67/
    dates.py                day-of-month logic
    naming.py                table/model naming
    model.py                  fit + evaluate (pandas/scikit-learn only)
    gate.py                    the RMSE promotion predicate
    checks.py                  data-quality expectations (Spark)
tests/
  conftest.py               local Spark session, skipped without Java 17+
  test_bundle_config.py     validates databricks.yml structure
  test_dates.py, test_naming.py, test_gate.py, test_model.py, test_checks.py
```

## Variables

| Variable | Default | Purpose |
|---|---|---|
| `catalog` | `ctl_training_dev` | catalog read/written by ingest/train/validate/infer |
| `rmse_threshold` | `5.0` | max RMSE for a new model to be promoted |
| `cluster_id` | `0318-031919-b3fa4xtr` | existing all-purpose cluster every task runs on |

## Deploy

```
databricks bundle deploy -t dev
```

Requires `DATABRICKS_HOST` + `DATABRICKS_TOKEN` (PAT auth). GitHub Actions:
- `validate.yml` runs `databricks bundle validate -t dev` on every pull request.
- `test.yml` and `deploy.yml` are `workflow_dispatch`-triggered — run manually from the Actions tab.

## Tests

```
pip install -r requirements-dev.txt
python -m pytest -v
```

Tests marked `spark` need a local JVM (Java 17+); without one they skip with an explanatory message instead of failing.
