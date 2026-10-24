import json
from schemas import Invoice

#1: Rules:
system_instructions = """Your task is to help extract invoice data from the provided document and format into a clean JSON object
    Please keep this simple guidelines in mind:
    -> stick strictly to what is written in the document. Don't assume or create any details by yourself.
    -> if an optional piece of information is missing, just set its value to null.
    -> format all days as DD-MM-YYYY, if you run into an ambigous date like 2026/10/21, treat it as YYYY/MM/DD.
    -> keep numbers clean: no dollar signs, commas or other currency symbols. 
    -> use standard 3 letter ISO codes for currencies like INR, USD or EUR.
    -> provide only the raw JSON data.
    -> please skip any conversational filter, intro text, markdown styling or code blocks.
    -> If the document lists tax or a discount, put those amounts in tax_amount and discount_amount.
    -> total_amount is the final amount payable stated on the document.
    -> If the document is not an invoice, return exactly {"error": "not_an_invoice"} and nothing else.
"""

#2 Few examples
examples = [
    {
        "input": """XYZ Web Services Pvt. Ltd
        Invoice No: INV-2026-0042
        Date: 22th Oct 2026
        Billed to: Sharma Traders

        Web hosting (annual plan)     1 X 24,000.00
        Domain renewwal (.com)        2 X 786.00
        Total due: INR 25,572""",
            "output": {
                "invoice_number": "INV-2026-0042",
                "date": "22-10-2026",
                "vendor_name": "XYZ Web Services Pvt. Ltd",
                "customer_name": "Sharma Traders",
                "items": [
                    {"description": "Web hosting (annual plan)", "quantity": 1, "unit_price": 24000.00},
                    {"description": "Domain renewal (.com)", "qantity": 2, "unit_price": 786.00},
                ],
                "total_amount": 25572.00,
                "currency": "INR",
            },
    },
    {
        "input": """Freelance invoice
        From: Raju Design
        #0087    2025/10/03
        Logo design - 3 hrs @ $45/hr
        Brand guide - 1 @ $120
        TOTAL: $255""",
            "output": {
            "invoice_number": "0087",
            "date": "03-10-2026",
            "vendor_name": "Raju Design",
            "customer_name": None,
            "items": [
                {"description": "Logo design", "quantity": 3, "unit_price": 45.0},
                {"description": "Brand guide", "quantity": 1, "unit_price": 120.0},
            ],
            "total_amount": 255.0,
            "currency": "USD",
        },
    },
    {
        "input": """Hi Rohan, are we still meeting on Friday at 4pm?
        Let me know if the conference room is free.""",
            "output": {"error": "not_an_invoice"},
    },
]

def format_examples() -> str:
    blocks = []
    for i, ex in enumerate(examples, start=1):
        blocks.append(
            f"### Example {i}\n"
            f"Document:\n{ex['input']}\n\n"
            f"JSON:\n{json.dumps(ex['output'], indent=2)}"
        )
        return "\n\n".join(blocks)

# Buider
def build_prompt(document_text: str, previous_error: str | None = None) -> str:
    schema = json.dumps(Invoice.model_json_schema(), indent=2)

    prompt = (
        f"{system_instructions}\n\n"
        f"JSON schema to follow:\n{schema}\n\n"
        f"{format_examples()}\n\n"
    )

    if previous_error:
        prompt += (
            "Your previous attempt was rejected with this validation error:\n"
            f"{previous_error}\n"
            "Fix the problem and return corrected JSON.\n\n"
        )
    prompt += (
        "### Now extract from this document\n"
        f"Document:\n{document_text}\n\n"
        "Return only the JSON object:"
    )  
    return prompt    

