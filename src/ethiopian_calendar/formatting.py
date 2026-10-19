"""Amharic and English month and weekday names, formatting and parsing of Ethiopian dates.

Amharic spellings vary (for example ኅዳር/ህዳር, ታኅሣሥ/ታህሳስ). The forms below follow common printed usage and
should be confirmed by a translator before they appear on statutory documents.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from .core import EthiopianDate

Lang = Literal["am", "en"]

MONTHS_AM = (
    "መስከረም", "ጥቅምት", "ኅዳር", "ታኅሣሥ", "ጥር", "የካቲት", "መጋቢት",
    "ሚያዝያ", "ግንቦት", "ሰኔ", "ሐምሌ", "ነሐሴ", "ጳጉሜን",
)  # fmt: skip
MONTHS_EN = (
    "Meskerem", "Tikimt", "Hidar", "Tahsas", "Tir", "Yekatit", "Megabit",
    "Miazia", "Ginbot", "Sene", "Hamle", "Nehase", "Pagume",
)  # fmt: skip

# Indexed by date.weekday(): Monday = 0.
WEEKDAYS_AM = ("ሰኞ", "ማክሰኞ", "ረቡዕ", "ሐሙስ", "አርብ", "ቅዳሜ", "እሑድ")
WEEKDAYS_EN = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def month_name(month: int, lang: Lang = "am") -> str:
    if not 1 <= month <= 13:
        raise ValueError(f"Ethiopian month must be 1..13, got {month}")
    return (MONTHS_AM if lang == "am" else MONTHS_EN)[month - 1]


def weekday_name(d: date, lang: Lang = "am") -> str:
    return (WEEKDAYS_AM if lang == "am" else WEEKDAYS_EN)[d.weekday()]


def format_ec(ec: EthiopianDate, style: Literal["long", "short", "iso"] = "long", lang: Lang = "am") -> str:
    """long: 'መስከረም 1 2019' / 'Meskerem 1, 2019'; short: '1/1/2019'; iso: '2019-01-01'."""
    if style == "iso":
        return ec.isoformat()
    if style == "short":
        return f"{ec.day}/{ec.month}/{ec.year}"
    if style != "long":
        raise ValueError(f"unknown style {style!r}")
    name = month_name(ec.month, lang)
    return f"{name} {ec.day} {ec.year}" if lang == "am" else f"{name} {ec.day}, {ec.year}"


def parse_ec(text: str) -> EthiopianDate:
    """Parse ISO ('2019-01-01'), short ('1/1/2019') or long ('መስከረም 1 2019', 'Meskerem 1, 2019')."""
    t = text.strip()
    if "-" in t and t.replace("-", "").isdigit():
        return EthiopianDate.parse(t)
    if "/" in t:
        try:
            d, m, y = (int(p) for p in t.split("/"))
        except ValueError:
            raise ValueError(f"cannot parse Ethiopian date {text!r}") from None
        return EthiopianDate(y, m, d)
    parts = t.replace(",", " ").split()
    if len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
        names = {n: i for i, n in enumerate(MONTHS_AM, 1)}
        names |= {n.lower(): i for i, n in enumerate(MONTHS_EN, 1)}
        month = names.get(parts[0]) or names.get(parts[0].lower())
        if month:
            return EthiopianDate(int(parts[2]), month, int(parts[1]))
    raise ValueError(f"cannot parse Ethiopian date {text!r}")
