from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader

PDF_PATH = Path(__file__).parent / "data" / "Ramayana_for_children.pdf"

PAGE_OFFSET = 1
MIN_CHARS = 100          
SKIP_INDEXES = {1, 46, 47}   


def load_pages(pdf_path: Path) -> list[Document]:
    reader = PdfReader(str(pdf_path))
    documents = []
    for index, page in enumerate(reader.pages):
        text = (page.extract_text() or "").strip()
        if index in SKIP_INDEXES or len(text) < MIN_CHARS:
            continue
        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": pdf_path.name,
                    "pdf_index": index,
                    "page": index - PAGE_OFFSET,
                },
            )
        )
    return documents


if __name__ == "__main__":
    docs = load_pages(PDF_PATH)
    print(f"Kept {len(docs)} usable pages\n")
    for doc in docs:
        meta = doc.metadata
        start = doc.page_content[:50].replace("\n", " ")
        print(f"page {meta['page']:>2} | index {meta['pdf_index']:>2} | {len(doc.page_content):>5} chars | {start}")