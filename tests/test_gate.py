"""Unit tests over the RMSE gate in room67/gate.py."""

from room67.gate import exceeds_threshold


def test_rmse_under_threshold_passes():
    assert exceeds_threshold(3.0, 5.0) is False


def test_rmse_over_threshold_fails():
    assert exceeds_threshold(6.0, 5.0) is True


def test_rmse_equal_to_threshold_passes():
    """The gate promotes at the boundary, it does not just tolerate it."""
    assert exceeds_threshold(5.0, 5.0) is False
