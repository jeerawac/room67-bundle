"""Regression diagnostic figure: predicted vs actual fare_amount.

Plain arrays in, a Figure out — no Spark, no I/O — so the same function
train_demo.py logs to MLflow is exercised by tests/test_plots.py on a
GitHub runner.
"""

import matplotlib

matplotlib.use("Agg")          # no display on a runner or a driver
import matplotlib.pyplot as plt  # noqa: E402


def figure_predicted_vs_actual(actual, predicted):
    """Scatter of predicted vs actual, with the y = x line a perfect model
    would sit on. Points scattered around that line is what a working
    fare_amount ~ trip_distance fit looks like; a flat cloud or a shifted
    line is what a broken one looks like."""
    lo = min(min(actual), min(predicted))
    hi = max(max(actual), max(predicted))

    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.scatter(actual, predicted, alpha=0.4, s=12, color="tab:blue")
    ax.plot([lo, hi], [lo, hi], "k--", linewidth=1, label="y = x")
    ax.set_xlabel("actual fare_amount")
    ax.set_ylabel("predicted fare_amount")
    ax.set_title("Predicted vs actual")
    ax.legend()
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    return fig
