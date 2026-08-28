"""Tests over the data-quality expectations in room67/checks.py.

These expectations are what audit_quality.py runs against the real table
after every ingest. These tests prove the expectations themselves work: each
one is shown passing on a clean fixture and catching an injected fault.
"""

import pytest

from room67.checks import audit, completeness_violations, validity_violations, volume_violations

pytestmark = pytest.mark.spark


def test_a_clean_frame_raises_nothing(trips_frame):
    assert audit(trips_frame) == []


def test_completeness_catches_an_injected_null(spark, trips_frame):
    dirty = trips_frame.union(
        spark.createDataFrame([(None, 10.0)], trips_frame.schema))
    assert completeness_violations(dirty, ["trip_distance"]) == [
        "completeness: trip_distance has 1 null value(s)"]


def test_validity_catches_a_negative_fare(spark, trips_frame):
    dirty = trips_frame.union(
        spark.createDataFrame([(1.0, -5.0)], trips_frame.schema))
    assert validity_violations(dirty, "fare_amount", 0) == [
        "validity: fare_amount has 1 value(s) below 0"]


def test_volume_catches_the_empty_frame(spark, trips_frame):
    """An empty frame passes every column-level expectation, which is why a
    row-count expectation has to exist."""
    empty = spark.createDataFrame([], trips_frame.schema)
    assert completeness_violations(empty, ["trip_distance"]) == []
    assert volume_violations(empty, 1) == ["volume: 0 row(s), expected at least 1"]


def test_the_full_audit_reports_every_fault_at_once(spark, trips_frame):
    dirty = trips_frame.union(
        spark.createDataFrame([(-1.0, None)], trips_frame.schema))
    reported = audit(dirty)
    assert len(reported) == 2
    assert any(v.startswith("completeness: fare_amount") for v in reported)
    assert any(v.startswith("validity: trip_distance") for v in reported)
