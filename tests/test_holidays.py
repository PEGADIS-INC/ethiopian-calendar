from datetime import date

import pytest

from ethiopian_calendar import holidays_between, orthodox_easter


@pytest.mark.parametrize(
    "year,expected",
    [(2022, (4, 24)), (2023, (4, 16)), (2024, (5, 5)), (2025, (4, 20)), (2026, (4, 12)), (2027, (5, 2))],
)
def test_orthodox_easter_known_dates(year, expected):
    assert orthodox_easter(year) == date(year, *expected)


def test_efy_2019_defaults():
    found = {h.key: h.date for h in holidays_between(date(2026, 7, 8), date(2027, 7, 7))}
    assert found["enkutatash"] == date(2026, 9, 11)
    assert found["meskel"] == date(2026, 9, 27)
    assert found["genna"] == date(2027, 1, 7)
    assert found["timkat"] == date(2027, 1, 19)
    assert found["adwa"] == date(2027, 3, 2)
    assert found["siklet"] == date(2027, 4, 30)
    assert found["fasika"] == date(2027, 5, 2)
    assert found["labour_day"] == date(2027, 5, 1)
    assert found["patriots"] == date(2027, 5, 5)  # Miazia 27
    assert found["derg_downfall"] == date(2027, 5, 28)  # Ginbot 20


def test_sorted_bounded_and_unique():
    hs = holidays_between(date(2026, 7, 8), date(2027, 7, 7))
    assert hs == sorted(hs)
    assert all(date(2026, 7, 8) <= h.date <= date(2027, 7, 7) for h in hs)
    assert len({(h.key, h.date) for h in hs}) == len(hs)
    assert all(h.name_am and h.name_en for h in hs)


def test_empty_range():
    assert holidays_between(date(2026, 10, 1), date(2026, 10, 2)) == []
