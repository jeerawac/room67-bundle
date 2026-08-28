# room67-bundle

Databricks Asset Bundle demo: monthly retrain + daily inference pipeline on the NYC taxi sample dataset, gated by RMSE.

## Pipeline

Job `namaew_job` runs daily (`0 0 2 * * ?` UTC):

1. **check_date** — reads day of month, sets task value.
2. **gate_retrain** — condition task, true only on the 1st.
3. If retrain gate true: **ingest** → **train** → **validate**
   - `ingest_nyctaxi.py`: copies a 5000-row slice of `samples.nyctaxi.trips` into `{catalog}.m3.namaew_trips_raw`.
   - `train_demo.py`: fits `LinearRegression` (fare_amount ~ trip_distance), logs run + registers model to Unity Catalog as `{catalog}.m3.namaew_fare_model`.
   - `validate_demo.py`: fails the run if RMSE > `rmse_threshold`; otherwise aliases the new version `champion`.
4. **infer** — runs `run_if: ALL_DONE` after gate/validate; scores current `champion` model against raw table, writes to `{catalog}.m3.namaew_predictions`. Skips gracefully (writes a `status="skipped"` row) if no champion exists yet.

Separate job `run_tests_job` runs the pytest suite (`run_tests.py`) on a job cluster — CI check without local Databricks Connect.

## Repo layout

```
databricks.yml        bundle config, includes resources/*.yml
resources/
  namaew_job.yml       main pipeline job
  run_tests_job.yml    CI test job
src/
  check_date.py       gate: day-of-month check
  ingest_nyctaxi.py    ingest sample data
  train_demo.py        train + register model
  validate_demo.py     RMSE gate + promote to champion
  infer_demo.py         score champion model
  run_tests.py          CI entrypoint, runs pytest on-cluster
tests/
  conftest.py
  test_bundle_config.py  validates databricks.yml structure
  test_check_date.py     validates check_date logic
```

## Variables

| Variable | Default | Purpose |
|---|---|---|
| `catalog` | `ctl_training_dev` | catalog read/written by ingest/train/validate/infer |
| `rmse_threshold` | `5.0` | max RMSE for a new model to be promoted |

## Deploy

```
databricks bundle deploy -t dev
```

Requires `DATABRICKS_HOST` + `DATABRICKS_TOKEN` (PAT auth). GitHub Actions workflows (`test.yml`, `deploy.yml`) are `workflow_dispatch`-triggered — run manually from the Actions tab.

## Tests

```
pip install pytest pyyaml
python -m pytest -v
```
