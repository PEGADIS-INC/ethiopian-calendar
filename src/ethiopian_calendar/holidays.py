"""Default public holidays. These are DEFAULTS for planning and demo data, not an official list.

The Ethiopian government announces each year's holidays; movable and religious days can differ from the
rules below by a day. Applications must let an accountant confirm or override the list for each year.

Rules used:
- EC-anchored: Enkutatash (Meskerem 1), Meskel (Meskerem 17), Adwa Victory (Yekatit 23),
  Patriots' Victory (Miazia 27), Downfall of the Derg (Ginbot 20).
- Gregorian-anchored: Labour Day (1 May).
- Julian-anchored (the Orthodox Church calendar): Genna (25 Dec Julian), Timkat (6 Jan Julian),
  Siklet and Fasika (Julian computus). Julian-to-Gregorian offset is 13 days, valid 1900-03-01 to 2100-02-28.
Islamic holidays (Eid al-Fitr, Eid al-Adha, Mawlid) depend on moon sighting and are not computed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from .core import ec_to_gc, gc_to_ec

_JULIAN_TO_GREGORIAN_DAYS = 13
_VALID_FROM, _VALID_TO = date(1900, 3, 1), date(2100, 2, 28)


@dataclass(frozen=True, order=True)
class Holiday:
    date: date
    key: str
    name_en: str
    name_am: str


def _julian(year: int, month: int, day: int) -> date:
    d = date(year, month, day) + timedelta(days=_JULIAN_TO_GREGORIAN_DAYS)
    if not _VALID_FROM <= d <= _VALID_TO:
        raise ValueError(f"Julian-anchored holidays are only supported 1900-03-01 to 2100-02-28, got {d}")
    return d


def orthodox_easter(year: int) -> date:
    """Orthodox Easter (Fasika) as a Gregorian date, by the Julian computus (Meeus)."""
    a, b, c = year % 4, year % 7, year % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    month, day = divmod(d + e + 114, 31)
    return _julian(year, month, day + 1)


def _candidates(gc_year: int) -> list[Holiday]:
    easter = orthodox_easter(gc_year)
    return [
        Holiday(_julian(gc_year, 12, 25), "genna", "Genna (Ethiopian Christmas)", "ገና"),
        Holiday(_julian(gc_year, 1, 6), "timkat", "Timkat (Epiphany)", "ጥምቀት"),
        Holiday(easter - timedelta(days=2), "siklet", "Siklet (Good Friday)", "ስቅለት"),
        Holiday(easter, "fasika", "Fasika (Easter)", "ፋሲካ"),
        Holiday(date(gc_year, 5, 1), "labour_day", "International Labour Day", "የሠራተኞች ቀን"),
    ]


def _ec_anchored(ec_year: int) -> list[Holiday]:
    return [
        Holiday(ec_to_gc(ec_year, 1, 1), "enkutatash", "Enkutatash (Ethiopian New Year)", "እንቁጣጣሽ"),
        Holiday(ec_to_gc(ec_year, 1, 17), "meskel", "Meskel (Finding of the True Cross)", "መስቀል"),
        Holiday(ec_to_gc(ec_year, 6, 23), "adwa", "Adwa Victory Day", "የአድዋ ድል በዓል"),
        Holiday(ec_to_gc(ec_year, 8, 27), "patriots", "Patriots' Victory Day", "የአርበኞች ቀን"),
        Holiday(ec_to_gc(ec_year, 9, 20), "derg_downfall", "Downfall of the Derg", "ግንቦት 20"),
    ]


def holidays_between(start: date, end: date) -> list[Holiday]:
    """Default holidays from `start` to `end` inclusive, sorted by date."""
    found: dict[tuple[date, str], Holiday] = {}
    for gc_year in range(start.year - 1, end.year + 2):
        try:
            for h in _candidates(gc_year):
                found[(h.date, h.key)] = h
        except ValueError:
            continue
    for ec_year in range(max(1, gc_to_ec(start).year - 1), gc_to_ec(end).year + 2):
        for h in _ec_anchored(ec_year):
            found[(h.date, h.key)] = h
    return sorted(h for h in found.values() if start <= h.date <= end)
