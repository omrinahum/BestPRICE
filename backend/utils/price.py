# Utility functions for price-related operations
from decimal import Decimal

def to_decimal(value) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal("0.0")

def normalize_currency(currency: str) -> str:
    return currency.upper() if currency else "USD" 