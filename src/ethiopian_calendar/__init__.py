"""Ethiopian calendar library. Pure Python; must not import Frappe."""

__version__ = "0.1.0"

from .core import EthiopianDate, days_in_month, ec_to_gc, gc_to_ec, is_leap_year  # noqa: E402
from .fiscal import FiscalYear, Period, fiscal_year, fiscal_year_of, periods  # noqa: E402
from .formatting import format_ec, month_name, parse_ec, weekday_name  # noqa: E402
from .holidays import Holiday, holidays_between, orthodox_easter  # noqa: E402

__all__ = [
    "EthiopianDate", "FiscalYear", "Holiday", "Period", "days_in_month", "ec_to_gc", "fiscal_year",
    "fiscal_year_of", "format_ec", "gc_to_ec", "holidays_between", "is_leap_year", "month_name",
    "orthodox_easter", "parse_ec", "periods", "weekday_name", "__version__",
]  # fmt: skip
