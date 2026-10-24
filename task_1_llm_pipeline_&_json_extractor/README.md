# Task 1: Structured LLM Prompt Pipeline & JSON Extractor

Extracts structured data from unstructured invoice text using the Google Gemini
API and guarantees the output is valid by checking it with Pydantic and
retrying with the error message when it isn't.

## How it works

```
text file -> build_prompt() -> Gemini API -> JSON -> Pydantic validation -> Invoice -> outputs/*.json
                                                          | (fails)
                                              retry with the error fed back (max 3)

main()
  ├─ check API key + file exist        (fail fast, clear message)
  ├─ read file, create client
  └─ extract()  ── loop up to 3 times ──┐
        build_prompt(text, previous_error)
        call Gemini
        validate with Pydantic
          ├─ OK → return Invoice  ─────────────→ save to outputs/
          ├─ ValidationError → store error → loop again (prompt now includes it)
          └─ APIError → retryable? sleep and loop : raise                                       
```

1. **Prompt**: rules + schema + two few shot examples + the document.
2. **Constrain**: JSON mode (`response_mime_type`), `temperature=0`.
3. **Verify**: Pydantic checks types, formats, and business rules.
4. **Recover**: on a validation failure the error text goes back into the next prompt; on rate limits (429/500/503) it waits with exponential backoff; on other API errors (bad key, bad model) it stops immediately.

## Project structure

```
task_1_llm_pipeline_&_json_extractor/
├── extractor.py        # CLI entry point: read, call API, validate, retry, save
├── schemas.py          # Pydantic models + validators
├── prompts.py          # prompt template and few-shot examples
├── test_schemas.py     # offline tests (no API key needed)
├── samples/            # input invoices (fake data)
├── outputs/            # extracted JSON results
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
# edit .env and set GEMINI_API_KEY=<your key from Google AI Studio>
```

Optional: set `GEMINI_MODEL` in `.env` to change the model (default `gemini-2.5-flash`).

## Usage

```bash
python extractor.py samples/invoice1.txt
```

## Example

**Input** (`samples/invoice1.txt`):
```
<<PASTE YOUR REAL invoice1.txt>>
```

**Output** (`outputs/invoice1.json`):
```json
<<PASTE YOUR REAL invoice1.json>>
```

## Validation rules

| Rule | Where | Why |
|---|---|---|
| Date must be a real `DD-MM-YYYY` date | `field_validator` | A regex alone accepts `31-02-2025` |
| `quantity > 0`, `unit_price >= 0` | `Field` constraints | Rejects nonsense values |
| At least one line item | `min_length=1` | A non-invoice can't pass as an empty invoice |
| Currency is a 3-letter code | regex | Caught a bug where the model returned `1.0` |
| Items + tax - discount = total (within 0.01) | `model_validator` | Catches misread numbers |

Run the tests with `pip install pytest` then `pytest -v`. <<5>> tests pass.

## Results on sample documents

| Sample | What it tests | Attempts | Result |
|---|---|---|---|
| invoice1 | <<baseline>> | <<1>> | <<correct / wrong: say what>> |
| invoice2 | <<...>> | <<...>> | <<...>> |
| invoice3 | <<...>> | <<...>> | <<...>> |
| invoice4 | <<...>> | <<...>> | <<...>> |
| invoice5 | <<...>> | <<...>> | <<...>> |

## Retry loop in action

```
<<PASTE THE REAL LOG from the bad-total run>>
```

<<One or two sentences: did the model correct itself on attempt 2 or fail after 3 attempts? Why?>>

## Design decisions

- **Schema generated into the prompt** from `Invoice.model_json_schema()`, so the schema and prompt can't drift apart.
- **`temperature=0`** because extraction should be repeatable, not creative.
- **Optional fields** (`customer_name`, `tax_amount`, `discount_amount`) so the model isn't pushed to invent values.
- **Date format DD-MM-YYYY** to match Indian invoices; ISO (`YYYY-MM-DD`) would be better for databases.
- **Two failure types, two responses**: bad answers get a corrective retry, API trouble gets a wait.

## Known limitations

- `total_amount` uses `float`; production financial code should use `Decimal`.
- If the *document itself* is inconsistent (the stated total doesn't match its items), retrying can't fix it. A real system would flag it for human review.
- Only plain-text input; no PDF or image parsing.
- <<Add any real failure you observed in your samples.>>