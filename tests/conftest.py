"""One local Spark session for the whole suite: starting it is the expensive
part, so it is session-scoped.

Tests marked `spark` need a JVM. On a machine without one they are SKIPPED
with a single explanatory line rather than raising JAVA_GATEWAY_EXITED once
per test. CI sets ROOM67_REQUIRE_SPARK=1, which turns the skip back into a
failure: a runner silently skipping the Spark tests would be a gate that
proves less than it appears to.
"""

import os
import shutil
import subprocess

import pytest
from pyspark.sql import SparkSession


def _java_version():
    """The major version of the java on PATH, or None if there is none."""
    java = shutil.which("java")
    if not java:
        return None
    try:
        out = subprocess.run([java, "-version"], capture_output=True, text=True,
                             timeout=30).stderr
    except (OSError, subprocess.SubprocessError):
        return None
    for token in out.split():
        if token.startswith('"'):
            digits = token.strip('"').split(".")[0]
            return int(digits) if digits.isdigit() else None
    return None


def pytest_collection_modifyitems(config, items):
    version = _java_version()
    if version is not None and version >= 17:
        return
    if os.environ.get("ROOM67_REQUIRE_SPARK") == "1":
        return                      # CI: let the failure be a failure
    reason = (
        "no Java 17+ on this machine, so the Spark tests cannot run "
        "(sudo apt-get install -y openjdk-17-jre-headless). Everything else "
        "still runs, and CI runs the rest."
        if version is None else
        f"Java {version} is too old for pyspark 3.5.x; 17 or later is needed."
    )
    skip = pytest.mark.skip(reason=reason)
    for item in items:
        if "spark" in item.keywords:
            item.add_marker(skip)


@pytest.fixture(scope="session")
def spark():
    session = (SparkSession.builder
               .master("local[1]")
               .appName("room67-bundle-tests")
               .config("spark.ui.enabled", "false")
               .config("spark.sql.shuffle.partitions", "1")
               .getOrCreate())
    yield session
    session.stop()


@pytest.fixture
def trips_frame(spark):
    """A clean room67_trips_raw fixture: no nulls, no negative values."""
    rows = [
        (1.2, 8.5),
        (3.4, 15.0),
        (0.5, 5.0),
    ]
    return spark.createDataFrame(rows, "trip_distance double, fare_amount double")
