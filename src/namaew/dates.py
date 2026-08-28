"""Pure date logic: no clock inside the function itself, so the same input
always gives the same answer and the test suite never depends on today()."""

from datetime import date


def day_of_month(today: date) -> int:
    """The day-of-month the retrain gate compares against 1."""
    return today.day
