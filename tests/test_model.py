"""Tests over namaew/model.py: pandas and scikit-learn only, no Spark, so
these run on the GitHub runner exactly as train_demo.py runs on the cluster.
"""

import pandas as pd
import pytest

from namaew.model import fit_and_evaluate


def _linear_frame(n=40, noise=0.0):
    """trip_distance rising, fare_amount an exact linear function of it (plus
    optional noise), so the fit is checkable by hand."""
    distance = [0.5 * i for i in range(1, n + 1)]
    fare = [2.5 + 3.0 * d + noise for d in distance]
    return pd.DataFrame({"trip_distance": distance, "fare_amount": fare})


def test_fit_and_evaluate_is_deterministic_given_the_same_seed():
    frame = _linear_frame()
    _, rmse_a, _ = fit_and_evaluate(frame, random_state=1)
    _, rmse_b, _ = fit_and_evaluate(frame, random_state=1)
    assert rmse_a == rmse_b


def test_fit_and_evaluate_recovers_a_clean_linear_relationship():
    """No noise: the held-out RMSE should be ~0."""
    model, rmse, _ = fit_and_evaluate(_linear_frame())
    assert rmse < 1e-6
    prediction = model.predict(pd.DataFrame({"trip_distance": [10.0]}))[0]
    assert prediction == pytest.approx(2.5 + 3.0 * 10.0, abs=1e-6)


def test_fit_and_evaluate_splits_the_frame_by_test_size():
    frame = _linear_frame(n=40)
    _, _, train_df = fit_and_evaluate(frame, test_size=0.25)
    assert len(train_df) == 30
