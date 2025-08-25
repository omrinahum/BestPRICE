
import pytest
from decimal import Decimal
from backend.utils.price import to_decimal, normalize_currency

def test_to_decimal_various():
    """
    to_decimal: converts int, float, str, None into Decimal.
    """
    assert to_decimal(10) == Decimal("10")
    assert to_decimal(10.5) == Decimal("10.5")
    assert to_decimal("7.25") == Decimal("7.25")
    assert to_decimal(None) == Decimal("0.0")
    assert to_decimal("") == Decimal("0.0")

def test_normalize_currency_defaults():
    """
    normalize_currency: uppercases, defaults to USD for None or empty.
    """
    assert normalize_currency("usd") == "USD"
    assert normalize_currency("EUR") == "EUR"
    assert normalize_currency(None) == "USD"
    assert normalize_currency("") == "USD"
