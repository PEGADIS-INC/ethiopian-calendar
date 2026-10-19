# ethiopian-calendar

Pure-Python Ethiopian (EC) and Gregorian (GC) calendar library: conversion, leap years, Pagume, fiscal
periods (Hamle 1 to Sene 30), default holidays, and Amharic/English formatting. MIT licence. No dependencies.

## Install

```bash
pip install "ethiopian-calendar @ git+https://github.com/PEGADIS-INC/ethiopian-calendar@v0.1.0"
```

Requires Python 3.10 or newer. It is not on PyPI yet.

## Use

```python
from datetime import date
from ethiopian_calendar import (
    gc_to_ec, ec_to_gc, fiscal_year, periods, holidays_between, format_ec, parse_ec,
)

gc_to_ec(date(2026, 10, 18))                  # EthiopianDate(year=2019, month=2, day=8)
ec_to_gc(2019, 1, 1)                          # date(2026, 9, 11)
fiscal_year(2019)                             # Hamle 1 2018 .. Sene 30 2019 = 2026-07-08 .. 2027-07-07
periods(2019)                                 # 13 periods (Pagume separate); pagume="merge_previous" gives 12
holidays_between(date(2026, 7, 8), date(2027, 7, 7))
format_ec(gc_to_ec(date(2026, 10, 18)))       # 'ጥቅምት 8 2019'
format_ec(gc_to_ec(date(2026, 10, 18)), lang="en")   # 'Tikimt 8, 2019'
parse_ec("Meskerem 17, 2019")                 # EthiopianDate(2019, 1, 17)
```

An EC leap year is any year with `year % 4 == 3`; Pagume (month 13) then has 6 days, otherwise 5.
Fiscal years default to Hamle 1 to Sene 30 and are labelled by the EC year in which they end (EFY 2019).

**Holidays are defaults, not an official list.** The rules are documented in `holidays.py`: EC-anchored days,
Labour Day, and Julian-anchored Genna, Timkat, Siklet and Fasika (valid 1900-03-01 to 2100-02-28). Islamic
holidays depend on moon sighting and are not computed. Check each year's list against the official
announcement. Amharic names and month spellings should be reviewed by a translator before statutory use.

## Conformance fixtures

Two files in `tests/fixtures/`. `roundtrip_10000.csv` holds 10,000 `gc,ec` pairs (every 7th day from
1900-01-01); `fiscal_periods_2015_2030.csv` holds every fiscal period of EFY 2015 to 2030. They are generated
by `tools/generate_fixture.py` with a method independent of the library (walking year by year from the anchor
1 Meskerem 2019 EC = 11 Sep 2026), so agreement is a real check. Other implementations may run the same
files. `python tools/generate_fixture.py --check` fails if the checked-in files drift.

## Development

```bash
pip install -e . pytest
pytest -q
```
