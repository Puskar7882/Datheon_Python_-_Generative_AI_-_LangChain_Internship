from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class LineItem(BaseModel):
    description: str
    quantity: float = Field(gt=0)
    unit_price: float = Field(ge=0)


class Invoice(BaseModel):
    invoice_number: str
    date: str = Field(
        description="Date in DD-MM-YYYY format",
        pattern=r"^\d{2}-\d{2}-\d{4}$",
    )
    vendor_name: str
    customer_name: Optional[str] = None
    items: List[LineItem] = Field(min_length=1)
    tax_amount: Optional[float] = Field(default=None, ge=0, description="Total tax, if listed")
    discount_amount: Optional[float] = Field(default=None, ge=0, description="Total discount, if listed")
    total_amount: float = Field(description="Final amount payable, including tax, after discount")
    currency: str = Field(
        description="3-letter ISO code such as INR, USD, EUR",
        pattern=r"^[A-Z]{3}$",
    )

    @field_validator("date")
    @classmethod
    def date_must_be_real(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%d-%m-%Y")
        except ValueError:
            raise ValueError(f"'{value}' is not a real calendar date in DD-MM-YYYY format")
        return value

    @model_validator(mode="after")
    def total_must_match_items(self) -> "Invoice":
        subtotal = sum(item.quantity * item.unit_price for item in self.items)
        expected = subtotal + (self.tax_amount or 0) - (self.discount_amount or 0)
        if abs(expected - self.total_amount) > 0.01:
            raise ValueError(
                f"total_amount {self.total_amount} does not match items "
                f"(subtotal {subtotal}, tax {self.tax_amount}, "
                f"discount {self.discount_amount}, expected {expected})"
            )
        return self


if __name__ == "__main__":
    print(Invoice.model_json_schema())