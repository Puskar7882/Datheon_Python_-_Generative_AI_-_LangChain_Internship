import argparse
import sys

from google.genai import errors

from rag import answer_question, get_client
from vector_store import CHROMA_DIR, build_index, load_index


def ask(question: str, store, client) -> None:
    try:
        result = answer_question(question, store, client)
    except errors.APIError as e:
        print(f"API error {e.code}: {e.message}")
        return
    print(f"\n{result['answer']}")
    if result["pages"]:
        print("Sources: page " + ", ".join(str(p) for p in result["pages"]))
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description="Ask questions about the indexed PDF.")
    parser.add_argument("question", nargs="?", help="ask one question and exit")
    parser.add_argument("--rebuild", action="store_true", help="re-index the PDF first")
    args = parser.parse_args()

    store = build_index() if args.rebuild or not CHROMA_DIR.exists() else load_index()
    try:
        client = get_client()
    except RuntimeError as e:
        print(e)
        return 1

    if args.question:
        ask(args.question, store, client)
        return 0

    print("Ask about the document. Type 'quit' to exit.")
    while True:
        question = input("You: ").strip()
        if question.lower() in {"quit", "exit"}:
            return 0
        if question:
            ask(question, store, client)


if __name__ == "__main__":
    sys.exit(main())