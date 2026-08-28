"""Data-quality expectations for the ingested trips table.

Each function returns a LIST OF VIOLATION STRINGS rather than raising or
returning a boolean, so the same function serves two callers: pytest asserts
the list is empty against a fixture, and audit_quality.py fails the task and
reports the list against the real table (Write-Audit-Publish).
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def completeness_violations(df: DataFrame, columns) -> list:
    """No NULLs where the pipeline promises a value."""
    out = []
    for column in columns:
        n = df.filter(F.col(column).isNull()).count()
        if n:
            out.append(f"completeness: {column} has {n} null value(s)")
    return out


def validity_violations(df: DataFrame, column: str, lo: float) -> list:
    """trip_distance and fare_amount are never negative."""
    below = df.filter(F.col(column) < F.lit(lo)).count()
    if below:
        return [f"validity: {column} has {below} value(s) below {lo}"]
    return []


def volume_violations(df: DataFrame, min_rows: int) -> list:
    """An empty frame passes every column-level check ever written."""
    n = df.count()
    if n < min_rows:
        return [f"volume: {n} row(s), expected at least {min_rows}"]
    return []


def audit(df: DataFrame) -> list:
    """The full expectation suite for namaew_trips_raw, in one call."""
    return (
        volume_violations(df, 1)
        + completeness_violations(df, ["trip_distance", "fare_amount"])
        + validity_violations(df, "trip_distance", 0)
        + validity_violations(df, "fare_amount", 0)
    )
