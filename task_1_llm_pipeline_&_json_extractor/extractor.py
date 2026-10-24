import argparse
import logging
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from prompts import build_prompt
from schemas import Invoice

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.WARNING)
log = logging.getLogger(__name__)

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_RETRIES = 3
RETRYABLE_CODES = {429, 500, 503}
MAX_CHARS = 50_000
OUTPUT_DIR = Path(__file__).parent / "outputs"


def extract(text: str, client: genai.Client) -> Invoice:
    previous_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        prompt = build_prompt(text, previous_error)

        # Step 1: call the API
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0,
                ),
            )
        except errors.APIError as e:
            if e.code not in RETRYABLE_CODES:
                raise
            if attempt < MAX_RETRIES:
                wait = 2**attempt
                log.warning(
                    "Attempt %d: API error %s, waiting %ds", attempt, e.code, wait
                )
                time.sleep(wait)
            else:
                log.warning("Attempt %d: API error %s", attempt, e.code)
            continue

        # Step 2: validate the model's answer
        try:
            invoice = Invoice.model_validate_json(response.text or "")
        except ValidationError as e:
            previous_error = str(e)[:1000]
            log.warning("Attempt %d failed validation: %s", attempt, previous_error)
            continue

        log.info("Attempt %d succeeded", attempt)
        return invoice

    raise RuntimeError(f"Extraction failed after {MAX_RETRIES} attempts")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract structured invoice JSON from a text file."
    )
    parser.add_argument("file", type=Path, help="path to a .txt document")
    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log.error("GEMINI_API_KEY not found. Copy .env.example to .env and add your key.")
        return 1

    if not args.file.is_file():
        log.error("File not found: %s", args.file)
        return 1

    if args.file.suffix.lower() != ".txt":
        log.warning("Expected a .txt file, got '%s'. Trying anyway.", args.file.suffix)

    try:
        text = args.file.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError:
        log.error("%s is not a UTF-8 text file", args.file.name)
        return 1

    if not text:
        log.error("File is empty: %s", args.file)
        return 1
    if len(text) > MAX_CHARS:
        log.error("File too large (%d chars, limit %d)", len(text), MAX_CHARS)
        return 1

    client = genai.Client(api_key=api_key)

    try:
        invoice = extract(text, client)
    except (RuntimeError, errors.APIError) as e:
        log.error("Could not process %s: %s", args.file.name, e)
        return 1

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / f"{args.file.stem}.json"
    out_path.write_text(invoice.model_dump_json(indent=2), encoding="utf-8")

    print(invoice.model_dump_json(indent=2))
    log.info("Saved to %s", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())