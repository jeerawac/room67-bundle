"""Unit tests over the pure function in namaew/dates.py.

No Spark, no clock, no workspace. Milliseconds, and they run on every push.
"""

from datetime import date

from namaew.dates import day_of_month


def test_day_of_month_reads_the_day_field():
    assert day_of_month(date(2026, 8, 1)) == 1
    assert day_of_month(date(2026, 8, 28)) == 28


def test_day_of_month_at_the_end_of_a_short_month():
    assert day_of_month(date(2026, 2, 28)) == 28
