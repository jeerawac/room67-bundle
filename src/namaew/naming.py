"""Table and model naming, in one place so ingest/audit/train/validate/infer
name the same objects the same way instead of repeating the schema string."""

SCHEMA = "m3"


def trips_table(catalog: str) -> str:
    return f"{catalog}.{SCHEMA}.namaew_trips_raw"


def predictions_table(catalog: str) -> str:
    return f"{catalog}.{SCHEMA}.namaew_predictions"


def model_name(catalog: str) -> str:
    return f"{catalog}.{SCHEMA}.namaew_fare_model"
