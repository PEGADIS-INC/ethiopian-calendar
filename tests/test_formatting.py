from datetime import date

import pytest

from ethiopian_calendar import EthiopianDate, format_ec, month_name, parse_ec, weekday_name

D = EthiopianDate(2019, 1, 17)


def test_names():
    assert month_name(1) == "መስከረም" and month_name(13, "en") == "Pagume"
    assert weekday_name(date(2026, 10, 18), "en") == "Sunday"
    assert weekday_name(date(2026, 10, 18)) == "እሑድ"
    with pytest.raises(ValueError):
        month_name(0)


def test_formats():
    assert format_ec(D) == "መስከረም 17 2019"
    assert format_ec(D, lang="en") == "Meskerem 17, 2019"
    assert format_ec(D, "short") == "17/1/2019"
    assert format_ec(D, "iso") == "2019-01-17"
    with pytest.raises(ValueError):
        format_ec(D, "weird")  # type: ignore[arg-type]


@pytest.mark.parametrize("style,lang", [("long", "am"), ("long", "en"), ("short", "am"), ("iso", "en")])
def test_parse_round_trips_every_style(style, lang):
    for ec in (D, EthiopianDate(2019, 13, 6), EthiopianDate(2018, 11, 1)):
        assert parse_ec(format_ec(ec, style, lang)) == ec


@pytest.mark.parametrize("bad", ["", "Hello 1 2019", "ጳጉሜን 6 2018", "1/1", "2019-13-07"])
def test_parse_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        parse_ec(bad)
