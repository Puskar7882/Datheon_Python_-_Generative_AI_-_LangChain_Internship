import shutil
import sys
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from chunking import split_pages
from ingest import PDF_PATH, load_pages

CHROMA_DIR = Path(__file__).parent / "chroma_db"
COLLECTION = "ramayana"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200
MIN_CHUNK_CHARS = 80


def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )


def build_index() -> Chroma:
    """Delete any old index, then embed and store every chunk."""
    shutil.rmtree(CHROMA_DIR, ignore_errors=True)  
    pages = load_pages(PDF_PATH)
    chunks = [
        c
        for c in split_pages(pages, CHUNK_SIZE, CHUNK_OVERLAP)
        if len(c.page_content) >= MIN_CHUNK_CHARS
    ]
    print(f"Embedding {len(chunks)} chunks...")
    return Chroma.from_documents(
        chunks,
        get_embeddings(),
        collection_name=COLLECTION,
        persist_directory=str(CHROMA_DIR),
    )


def load_index() -> Chroma:
    """Open the saved index without re-embedding."""
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=get_embeddings(),
        persist_directory=str(CHROMA_DIR),
    )


TEST_QUESTIONS = [
    "Why did Kaikeyi ask for two boons?",         
    "Who is Sampati?",                            
    "Who stopped Ravana from killing Hanuman?",   
]

if __name__ == "__main__":
    if "--rebuild" in sys.argv or not CHROMA_DIR.exists():
        store = build_index()
    else:
        store = load_index()

    for question in TEST_QUESTIONS:
        print(f"\nQ: {question}")
        for doc, distance in store.similarity_search_with_score(question, k=4):
            snippet = doc.page_content[:110]
            print(f"   page {doc.metadata['page']:>2} | distance {distance:.3f} | {snippet}...")