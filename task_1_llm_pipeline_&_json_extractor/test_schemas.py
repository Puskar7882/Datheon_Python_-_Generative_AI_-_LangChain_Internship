import pytest
from pydantic import ValidationError

from schemas import Invoice

VALID = {
    "invoice_number": "INV-1",
    "date": "05-04-2025",
    "vendor_name": "ACME",
    "items": [{"description": "Thing", "quantity": 2, "unit_price": 50}],
    "total_amount": 100,
    "currency": "INR",
}


def test_valid_invoice_passes():
    assert Invoice(**VALID).total_amount == 100


def test_impossible_date_rejected():
    with pytest.raises(ValidationError):
        Invoice(**{**VALID, "date": "31-02-2025"})


def test_wrong_total_rejected():
    with pytest.raises(ValidationError):
        Invoice(**{**VALID, "total_amount": 999})


def test_tax_is_included_in_total():
    assert Invoice(**{**VALID, "tax_amount": 18, "total_amount": 118})


def test_empty_items_rejected():
    with pytest.raises(ValidationError):
        Invoice(**{**VALID, "items": []})

def test_placeholder_vendor_rejected():
    with pytest.raises(ValidationError):
        Invoice(**{**VALID, "vendor_name": "UNKNOWN"})


def test_xxx_currency_rejected():
    with pytest.raises(ValidationError):
        Invoice(**{**VALID, "currency": "XXX"})        