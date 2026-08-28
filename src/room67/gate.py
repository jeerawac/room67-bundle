"""The RMSE promotion gate: one pure predicate, so validate_demo.py calls it
instead of embedding the comparison inline."""


def exceeds_threshold(rmse: float, threshold: float) -> bool:
    return rmse > threshold
