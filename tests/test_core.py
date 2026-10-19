import csv
from datetime import date, timedelta
from pathlib import Path

import pytest

from ethiopian_calendar import EthiopianDate, days_in_month, ec_to_gc, gc_to_ec, is_leap_year

FIXTURE = Path(__file__).parent / "fixtures" / "roundtrip_10000.csv"


def test_known_anchors():
    assert gc_to_ec(date(2026, 9, 11)) == EthiopianDate(2019, 1, 1)  # Enkutatash 2019
    assert gc_to_ec(date(2026, 10, 18)) == EthiopianDate(2019, 2, 8)
    assert gc_to_ec(date(2026, 7, 8)) == EthiopianDate(2018, 11, 1)  # Hamle 1: fiscal year start
    assert gc_to_ec(date(2027, 7, 7)) == EthiopianDate(2019, 10, 30)  # Sene 30: fiscal year end
    assert gc_to_ec(date(2023, 9, 12)) == EthiopianDate(2016, 1, 1)  # year before a GC leap year
    assert gc_to_ec(date(2024, 9, 11)) == EthiopianDate(2017, 1, 1)


def test_leap_years_and_pagume():
    assert [y for y in range(2010, 2024) if is_leap_year(y)] == [2011, 2015, 2019, 2023]
    assert days_in_month(2018, 13) == 5
    assert days_in_month(2019, 13) == 6
    assert gc_to_ec(date(2023, 9, 11)) == EthiopianDate(2015, 13, 6)  # last day of a leap year
    assert gc_to_ec(date(2026, 9, 10)) == EthiopianDate(2018, 13, 5)
    assert all(days_in_month(2019, m) == 30 for m in range(1, 13))


def test_pagume_6_only_in_leap_years():
    with pytest.raises(ValueError):
        EthiopianDate(2018, 13, 6)
    EthiopianDate(2019, 13, 6)


@pytest.mark.parametrize(
    "args", [(2019, 0, 1), (2019, 14, 1), (2019, 1, 0), (2019, 1, 31), (0, 1, 1), (-5, 1, 1)]
)
def test_invalid_dates_rejected(args):
    with pytest.raises(ValueError):
        EthiopianDate(*args)


def test_parse_and_iso():
    assert EthiopianDate.parse("2019-01-01") == EthiopianDate(2019, 1, 1)
    assert str(EthiopianDate(2019, 2, 8)) == "2019-02-08"
    with pytest.raises(ValueError):
        EthiopianDate.parse("2019/01/01")


def test_ordering():
    assert EthiopianDate(2018, 13, 5) < EthiopianDate(2019, 1, 1)


def test_before_epoch_and_after_range_raise():
    with pytest.raises(ValueError):
        gc_to_ec(date(1, 1, 1))
    with pytest.raises(ValueError):
        ec_to_gc(9999, 1, 1)


def test_every_day_round_trips_and_advances_by_one():
    d = date(1990, 1, 1)
    prev = gc_to_ec(d)
    for i in range(1, 365 * 40):
        cur = gc_to_ec(d + timedelta(days=i))
        assert cur.to_gregorian() == d + timedelta(days=i)
        if cur.day != 1:
            assert (cur.year, cur.month, cur.day) == (prev.year, prev.month, prev.day + 1)
        else:
            assert prev.day == days_in_month(prev.year, prev.month)
        prev = cur


def test_fixture_has_10000_rows_and_matches_the_library():
    with FIXTURE.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 10_000
    assert len({r["gc"] for r in rows}) == 10_000
    for r in rows:
        gc = date.fromisoformat(r["gc"])
        ec = EthiopianDate.parse(r["ec"])
        assert gc_to_ec(gc) == ec, r
        assert ec_to_gc(ec.year, ec.month, ec.day) == gc, r
