"""Fiscal years and periods. Default: Hamle 1 to Sene 30 (month 11 to month 10 of the next EC year).

Fiscal years are labelled by the EC year in which they end (EFY 2019 = Hamle 1 2018 to Sene 30 2019,
8 Jul 2026 to 7 Jul 2027). A year that starts on Meskerem 1 is labelled by its own EC year.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

from .core import PAGUME, EthiopianDate, days_in_month, ec_to_gc, gc_to_ec

DEFAULT_START_MONTH = 11  # Hamle


@dataclass(frozen=True)
class Period:
    fiscal_year: int
    index: int  # 1-based position within the fiscal year
    ec_month: int  # EC month the period starts in
    start: date
    end: date  # inclusive

    @property
    def ec_start(self) -> EthiopianDate:
        return gc_to_ec(self.start)

    @property
    def ec_end(self) -> EthiopianDate:
        return gc_to_ec(self.end)

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1


@dataclass(frozen=True)
class FiscalYear:
    year: int
    start: date
    end: date  # inclusive

    @property
    def ec_start(self) -> EthiopianDate:
        return gc_to_ec(self.start)

    @property
    def ec_end(self) -> EthiopianDate:
        return gc_to_ec(self.end)

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1


def _check_start_month(start_month: int) -> None:
    if not 1 <= start_month <= PAGUME:
        raise ValueError(f"start_month must be 1..13, got {start_month}")


def _start_ec_year(efy: int, start_month: int) -> int:
    return efy if start_month == 1 else efy - 1


def fiscal_year_of(d: date | EthiopianDate, start_month: int = DEFAULT_START_MONTH) -> int:
    """The fiscal-year label (EFY) containing a date."""
    _check_start_month(start_month)
    ec = gc_to_ec(d) if isinstance(d, date) else d
    return ec.year + 1 if start_month > 1 and ec.month >= start_month else ec.year


def fiscal_year(efy: int, start_month: int = DEFAULT_START_MONTH) -> FiscalYear:
    _check_start_month(start_month)
    start = ec_to_gc(_start_ec_year(efy, start_month), start_month, 1)
    next_start = ec_to_gc(_start_ec_year(efy + 1, start_month), start_month, 1)
    return FiscalYear(efy, start, next_start - timedelta(days=1))


def periods(
    efy: int,
    start_month: int = DEFAULT_START_MONTH,
    pagume: Literal["separate", "merge_previous"] = "separate",
) -> list[Period]:
    """Monthly periods of a fiscal year, in order.

    Pagume (5 or 6 days) is its own period by default; "merge_previous" folds it into the period
    before it (or the one after, if the fiscal year starts on Pagume).
    """
    if pagume not in ("separate", "merge_previous"):
        raise ValueError(f"pagume must be 'separate' or 'merge_previous', got {pagume!r}")
    fy = fiscal_year(efy, start_month)
    ec_year = _start_ec_year(efy, start_month)
    raw: list[tuple[int, date, date]] = []
    month = start_month
    while True:
        start = ec_to_gc(ec_year, month, 1)
        end = start + timedelta(days=days_in_month(ec_year, month) - 1)
        raw.append((month, start, end))
        month += 1
        if month > PAGUME:
            month, ec_year = 1, ec_year + 1
        if end >= fy.end:
            break
    if pagume == "merge_previous":
        merged: list[tuple[int, date, date]] = []
        for m, s, e in raw:
            if m == PAGUME and merged:
                pm, ps, _ = merged[-1]
                merged[-1] = (pm, ps, e)
            else:
                merged.append((m, s, e))
        if merged[0][0] == PAGUME and len(merged) > 1:  # fiscal year begins on Pagume
            _, s0, _ = merged[0]
            m1, _, e1 = merged[1]
            merged = [(PAGUME, s0, e1), *merged[2:]]
        raw = merged
    return [Period(efy, i, m, s, e) for i, (m, s, e) in enumerate(raw, 1)]
