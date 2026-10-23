from pydantic import BaseModel, Field
from typing import List, Optional

class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float

class Invoice(BaseModel):
    invoice_number: str
    date: str = Field(description="DD-MM-YYYY")
    vendor_name: str
    customer_name: Optional[str] = None
    items: List[LineItem]
    total_amount: float
    currency: float

if __name__ == "__main__":
    print(Invoice.model_json_schema())