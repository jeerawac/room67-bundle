"""Unit tests over namaew/naming.py: ingest/train/validate/infer must all
resolve to the same table and model names for a given catalog."""

from namaew.naming import model_name, predictions_table, trips_table


def test_names_share_the_catalog_and_schema():
    catalog = "ctl_training_dev"
    assert trips_table(catalog) == "ctl_training_dev.m3.namaew_trips_raw"
    assert predictions_table(catalog) == "ctl_training_dev.m3.namaew_predictions"
    assert model_name(catalog) == "ctl_training_dev.m3.namaew_fare_model"


def test_names_follow_the_catalog():
    assert trips_table("other_catalog").startswith("other_catalog.")
