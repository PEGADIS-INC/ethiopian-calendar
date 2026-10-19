import csv
from datetime import date, timedelta
from pathlib import Path

import pytest

from ethiopian_calendar import EthiopianDate, fiscal_year, fiscal_year_of, gc_to_ec, periods

PERIODS = Path(__file__).parent / "fixtures" / "fiscal_periods_2015_2030.csv"


def test_efy_2019_is_hamle_to_sene():
    fy = fiscal_year(2019)
    assert (fy.start, fy.end) == (date(2026, 7, 8), date(2027, 7, 7))
    assert fy.ec_start == EthiopianDate(2018, 11, 1)
    assert fy.ec_end == EthiopianDate(2019, 10, 30)


def test_fiscal_year_of():
    assert fiscal_year_of(date(2026, 7, 7)) == 2018
    assert fiscal_year_of(date(2026, 7, 8)) == 2019
    assert fiscal_year_of(EthiopianDate(2018, 13, 5)) == 2019  # Pagume belongs to the year that follows
    assert fiscal_year_of(EthiopianDate(2019, 10, 30)) == 2019
    assert fiscal_year_of(EthiopianDate(2019, 11, 1)) == 2020


def test_configurable_start_month():
    fy = fiscal_year(2019, start_month=1)  # EC calendar year
    assert (fy.ec_start, fy.ec_end) == (EthiopianDate(2019, 1, 1), EthiopianDate(2019, 13, 6))
    assert fiscal_year_of(EthiopianDate(2019, 5, 5), start_month=1) == 2019
    with pytest.raises(ValueError):
        fiscal_year(2019, start_month=14)


@pytest.mark.parametrize("efy", range(2015, 2031))
def test_periods_tile_the_fiscal_year(efy):
    fy, ps = fiscal_year(efy), periods(efy)
    assert len(ps) == 13
    assert ps[0].start == fy.start and ps[-1].end == fy.end
    for a, b in zip(ps, ps[1:]):
        assert b.start == a.end + timedelta(days=1)
    assert sum(p.days for p in ps) == fy.days
    assert ps[0].ec_month == 11 and ps[2].ec_month == 13 and ps[-1].ec_month == 10
    assert all(gc_to_ec(p.start).day == 1 for p in ps)


def test_merge_pagume_gives_twelve_periods():
    ps = periods(2019, pagume="merge_previous")
    assert len(ps) == 12
    assert ps[1].ec_month == 12 and ps[1].days == 30 + 5  # Nehase + Pagume 2018 (5 days)
    assert ps[0].start == fiscal_year(2019).start and ps[-1].end == fiscal_year(2019).end
    with pytest.raises(ValueError):
        periods(2019, pagume="drop")


def test_fixture_matches_independent_reference():
    with PERIODS.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 16 * 13
    assert {int(r["efy"]) for r in rows} == set(range(2015, 2031))
    for r in rows:
        p = periods(int(r["efy"]))[int(r["index"]) - 1]
        assert (p.ec_month, p.start, p.end) == (
            int(r["ec_month"]), date.fromisoformat(r["start_gc"]), date.fromisoformat(r["end_gc"])
        ), r
