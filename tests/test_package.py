import importlib
import sys


def test_importable_and_versioned():
    import ethiopian_calendar

    assert ethiopian_calendar.__version__


def test_does_not_pull_in_frappe():
    importlib.import_module("ethiopian_calendar")
    assert "frappe" not in sys.modules
