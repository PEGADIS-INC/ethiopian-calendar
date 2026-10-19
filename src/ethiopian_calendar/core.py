"""Ethiopian (EC) <-> Gregorian (GC) conversion.

The EC year has 12 months of 30 days and Pagume (month 13) of 5 days, or 6 in a leap year.
A leap year is any EC year with year % 4 == 3; the extra day closes that year. Enkutatash
(1 Meskerem) therefore falls on 11 September GC, or 12 September in the EC year before a GC leap year.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

# JDN of 1 Meskerem of EC year 0, so that year numbers below count from the same origin as the formula.
_EPOCH = 1723856
_GC_ORDINAL_TO_JDN = 1721425

MONTHS_PER_YEAR = 13
PAGUME = 13


def is_leap_year(year: int) -> bool:
    """EC leap years are 3, 7, 11, ... (year % 4 == 3): Pagume has 6 days."""
    return year % 4 == 3


def days_in_month(year: int, month: int) -> int:
    if not 1 <= month <= MONTHS_PER_YEAR:
        raise ValueError(f"Ethiopian month must be 1..13, got {month}")
    if month < PAGUME:
        return 30
    return 6 if is_leap_year(year) else 5


@dataclass(frozen=True, order=True)
class EthiopianDate:
    year: int
    month: int
    day: int

    def __post_init__(self) -> None:
        if self.year < 1:
            raise ValueError(f"Ethiopian year must be >= 1, got {self.year}")
        if not 1 <= self.day <= days_in_month(self.year, self.month):
            raise ValueError(f"invalid Ethiopian date {self.year:04d}-{self.month:02d}-{self.day:02d}")

    @classmethod
    def from_gregorian(cls, d: date) -> EthiopianDate:
        return gc_to_ec(d)

    @classmethod
    def parse(cls, text: str) -> EthiopianDate:
        """Parse 'YYYY-MM-DD' (Ethiopian)."""
        try:
            y, m, d = (int(part) for part in text.split("-"))
        except ValueError:
            raise ValueError(f"expected an Ethiopian date as YYYY-MM-DD, got {text!r}") from None
        return cls(y, m, d)

    def to_gregorian(self) -> date:
        return ec_to_gc(self.year, self.month, self.day)

    def isoformat(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    def __str__(self) -> str:
        return self.isoformat()


def gc_to_ec(d: date) -> EthiopianDate:
    jdn = d.toordinal() + _GC_ORDINAL_TO_JDN
    r = (jdn - _EPOCH) % 1461
    n = r % 365 + 365 * (r // 1460)
    year = 4 * ((jdn - _EPOCH) // 1461) + r // 365 - r // 1460
    if year < 1:
        raise ValueError(f"{d.isoformat()} is before 1 Meskerem 1 EC")
    return EthiopianDate(year, n // 30 + 1, n % 30 + 1)


def ec_to_gc(year: int, month: int, day: int) -> date:
    ec = EthiopianDate(year, month, day)  # validates
    jdn = _EPOCH + 365 * ec.year + ec.year // 4 + 30 * (ec.month - 1) + ec.day - 1
    try:
        return date.fromordinal(jdn - _GC_ORDINAL_TO_JDN)
    except (ValueError, OverflowError):
        raise ValueError(f"Ethiopian date {ec} is outside the supported Gregorian range") from None
