from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ingest import PDF_PATH, load_pages


def split_pages(
    pages: list[Document], chunk_size: int = 800, chunk_overlap: int = 120) -> list[Document]:
    """Split each page into chunks; every chunk inherits its page's metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        keep_separator="end",
    )
    return splitter.split_documents(pages)


if __name__ == "__main__":
    pages = load_pages(PDF_PATH)

    for size in (300, 800, 1500):
        chunks = split_pages(pages, chunk_size=size, chunk_overlap=int(size * 0.15))
        lengths = [len(c.page_content) for c in chunks]
        print(f"\nchunk_size={size}: {len(chunks)} chunks, "
              f"avg {sum(lengths) // len(lengths)} chars, shortest {min(lengths)}")

        for chunk in chunks:
            text = chunk.page_content
            if "banishment of Rama" in text:
                together = "fool you are" in text
                print(f"   page {chunk.metadata['page']} | {len(text)} chars | "
                      f"also has Manthara's warning: {together}")

    sample = split_pages(pages, 800, 120)[10]
    print("\n--- sample chunk ---")
    print(sample.metadata)
    print(sample.page_content)