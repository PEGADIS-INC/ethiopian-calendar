"""Generate the conformance fixtures with a reference method independent of the library.

  roundtrip_10000.csv         10,000 gc,ec pairs
  fiscal_periods_2015_2030.csv  every fiscal period (Hamle 1 to Sene 30) of EFY 2015..2030, Pagume separate

The library converts with a Julian-day formula. This script instead walks year by year from a
well-known anchor (1 Meskerem 2019 EC = 11 September 2026 GC), adding 365 or 366 days (EC leap
year: year % 4 == 3) and 30-day months with a 5/6-day Pagume. Agreement between the two is the test.

    python tools/generate_fixture.py          # writes the fixture
    python tools/generate_fixture.py --check  # exit 1 if the checked-in file differs

Other implementations can run the same files to check that they agree with this one.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ANCHOR_GC = date(2026, 9, 11)
ANCHOR_EC_YEAR = 2019  # 1 Meskerem 2019 EC
COUNT = 10_000
STEP_DAYS = 7
START_GC = date(1900, 1, 1)
FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
OUT = FIXTURES / "roundtrip_10000.csv"
OUT_PERIODS = FIXTURES / "fiscal_periods_2015_2030.csv"
FIRST_EFY, LAST_EFY = 2015, 2030


def year_days(year: int) -> int:
    return 366 if year % 4 == 3 else 365


def reference_ec(d: date) -> tuple[int, int, int]:
    """EC (year, month, day) for a Gregorian date by walking from the anchor."""
    offset = (d - ANCHOR_GC).days
    year = ANCHOR_EC_YEAR
    while offset < 0:
        year -= 1
        offset += year_days(year)
    while offset >= year_days(year):
        offset -= year_days(year)
        year += 1
    return year, offset // 30 + 1, offset % 30 + 1


def rows() -> list[str]:
    out = ["gc,ec"]
    for i in range(COUNT):
        d = START_GC + timedelta(days=i * STEP_DAYS)
        y, m, dd = reference_ec(d)
        out.append(f"{d.isoformat()},{y:04d}-{m:02d}-{dd:02d}")
    return out


def reference_gc(year: int, month: int, day: int) -> date:
    """Gregorian date of an EC date by walking from the anchor (independent of the library)."""
    offset = (month - 1) * 30 + (day - 1)
    y = ANCHOR_EC_YEAR
    while y < year:
        offset += year_days(y)
        y += 1
    while y > year:
        y -= 1
        offset -= year_days(y)
    return ANCHOR_GC + timedelta(days=offset)


def period_rows() -> list[str]:
    """efy,index,ec_month,start_gc,end_gc for 13 periods per fiscal year, Hamle (11) first."""
    out = ["efy,index,ec_month,start_gc,end_gc"]
    for efy in range(FIRST_EFY, LAST_EFY + 1):
        order = [(11, efy - 1), (12, efy - 1), (13, efy - 1)] + [(m, efy) for m in range(1, 11)]
        for i, (m, y) in enumerate(order, 1):
            length = 30 if m < 13 else (6 if y % 4 == 3 else 5)
            start = reference_gc(y, m, 1)
            end = start + timedelta(days=length - 1)
            out.append(f"{efy},{i},{m},{start.isoformat()},{end.isoformat()}")
    return out


def main(argv: list[str]) -> int:
    files = {OUT: "\n".join(rows()) + "\n", OUT_PERIODS: "\n".join(period_rows()) + "\n"}
    if "--check" in argv:
        same = all(
            p.exists() and p.read_text(encoding="utf-8").replace("\r\n", "\n") == body
            for p, body in files.items()
        )
        return 0 if same else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    for path, body in files.items():
        path.write_text(body, encoding="utf-8", newline="\n")
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
