from pydantic import BaseModel, Field
from typing import List, Optional

class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float

class Invoice(BaseModel):
    invoice_number: str
    date: str = Field(
    description="Date in DD-MM-YYYY format",
    pattern=r"^(0[1-9]|[12]\d|3[01])-(0[1-9]|1[0-2])-\d{4}$",
)
    vendor_name: str
    customer_name: Optional[str] = None
    items: List[LineItem]
    total_amount: float
    currency: str = Field(
        description="3-letter ISO code such as INR, USD, EUR",
        pattern=r"^[A-Z]{3}$",
    )

if __name__ == "__main__":
    print(Invoice.model_json_schema())