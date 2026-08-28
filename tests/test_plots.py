"""Tests over room67/plots.py: plain arrays, no Spark, no workspace, so the
same figure train_demo.py logs to MLflow is exercised on a GitHub runner.
"""

from room67.plots import figure_predicted_vs_actual


def test_figure_predicted_vs_actual_returns_a_non_empty_figure():
    actual = [10.0, 20.0, 30.0]
    predicted = [11.0, 19.0, 31.0]
    fig = figure_predicted_vs_actual(actual, predicted)
    ax = fig.axes[0]
    assert len(ax.collections) == 1          # the scatter
    assert len(ax.collections[0].get_offsets()) == len(actual)


def test_figure_predicted_vs_actual_draws_the_y_equals_x_reference_line():
    fig = figure_predicted_vs_actual([1.0, 5.0], [2.0, 4.0])
    ax = fig.axes[0]
    assert len(ax.lines) == 1
    xdata, ydata = ax.lines[0].get_data()
    assert list(xdata) == list(ydata)
