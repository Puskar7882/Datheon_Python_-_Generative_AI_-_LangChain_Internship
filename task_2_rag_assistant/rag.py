import os
import re
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from langchain_core.documents import Document

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
TOP_K = 4
MAX_RETRIES = 3
RETRYABLE_CODES = {429, 500, 503}
NOT_FOUND = "I don't know based on the provided document."

SYSTEM_INSTRUCTION = f"""You answer questions about a document using ONLY the context excerpts provided.
Rules:
- Use only facts stated in the context. Do not use outside knowledge even if you recognise the story.
- If the context does not contain the answer, reply with exactly: {NOT_FOUND}
- After each claim, cite the page like [p. 10]. Only cite pages shown in the context.
- Be concise: 1 to 4 sentences. The text comes from OCR and may contain errors; read through them."""


def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found. Add it to a .env file.")
    return genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})


def format_context(docs: list[Document]) -> str:
    return "\n\n".join(f"[Page {d.metadata['page']}]\n{d.page_content}" for d in docs)


def generate(prompt: str, client: genai.Client) -> str:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0,
                ),
            )
            return (response.text or "").strip()
        except errors.APIError as e:
            if e.code not in RETRYABLE_CODES or attempt == MAX_RETRIES:
                raise
            time.sleep(2**attempt)
    return ""


def answer_question(question: str, store, client: genai.Client) -> dict:
    docs = store.similarity_search(question, k=TOP_K)
    prompt = f"Context:\n{format_context(docs)}\n\nQuestion: {question}\nAnswer:"
    answer = generate(prompt, client) or "The model returned no text."

    if answer.startswith(NOT_FOUND):
        return {"answer": NOT_FOUND, "pages": []}

    retrieved = {d.metadata["page"] for d in docs}
    cited = {int(p) for p in re.findall(r"\[p\.\s*(\d+)\]", answer)}
    return {"answer": answer, "pages": sorted(cited & retrieved)}


def build_prompt(question: str, docs: list[Document], history: list[dict] | None = None) -> str:
    """Context + recent chat turns + the new question."""
    turns = ""
    if history:
        lines = [f"{m['role'].capitalize()}: {m['content']}" for m in history]
        turns = "Conversation so far:\n" + "\n".join(lines) + "\n\n"
    return f"Context:\n{format_context(docs)}\n\n{turns}Question: {question}\nAnswer:"


def stream_generate(prompt: str, client: genai.Client):
    """Yield the answer text piece by piece as Gemini produces it."""
    stream = client.models.generate_content_stream(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0,
        ),
    )
    for chunk in stream:
        if chunk.text:
            yield chunk.text


def finalize(answer: str, docs: list[Document]) -> dict:
    """Same citation checks as answer_question, for an already-complete answer."""
    answer = answer.strip()
    if not answer or answer.startswith(NOT_FOUND):
        return {"answer": NOT_FOUND, "pages": []}
    retrieved = {d.metadata["page"] for d in docs}
    cited = {int(p) for p in re.findall(r"\[p\.\s*(\d+)\]", answer)}
    return {"answer": answer, "pages": sorted(cited & retrieved)}