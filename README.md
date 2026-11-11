# Datheon Python + Generative AI & LangChain Internship

Projects completed for the Datheon virtual internship (October to November 2026).
Each task lives in its own folder with its own README, setup steps, and tests.

**Author:** Puskar Gayen

## Tasks

| Task | What it does | Stack | Status |
|---|---|---|---|
| [Task 1: Structured LLM Pipeline & JSON Extractor](./task_1_llm_pipeline_%26_json_extractor) | Extracts invoice data from unstructured text into validated JSON with corrective retries and a "not an invoice" path | Gemini, Pydantic | Done |
| [Task 2: Document Q&A Assistant (RAG)](./task_2_rag_assistant) | Answers questions strictly from a PDF, cites the page and says "I don't know" when the document has no answer | ChromaDB, local embeddings, Gemini | Done |
| Task 4: Streamlit Chatbot | Web UI with streaming and memory | Streamlit | Planned |

## Highlights

- **Verify, don't trust.** Task 1 checks every model answer with Pydantic (real dates, positive quantities, totals that add up) and feeds the error back to the model on a retry.
- **Grounded answers.** Task 2 answers only from retrieved text, cites printed page numbers and discards any page the model cites but was never retrieved.
- **Honest failures.** Both READMEs document real problems found while testing such as a retry loop that pushed the model to invent data and a PDF page lost to OCR that the system correctly declined to guess.
- **Offline tests.** Both tasks have tests that need no API key.

## Repository structure

```
.
├── task_1_llm_pipeline_&_json_extractor/
│   ├── extractor.py, schemas.py, prompts.py
│   ├── samples/, outputs/
│   └── README.md
├── task_2_rag_assistant/
│   ├── ingest.py, chunking.py, vector_store.py, rag.py, app.py
│   ├── data/                  # put your own PDF here
│   └── README.md
├── .env.example
└── .gitignore
```

## Quick start

Each task has its own `requirements.txt`, so use a separate virtual environment per task.

```bash
# Task 1
cd "task_1_llm_pipeline_&_json_extractor"
pip install -r requirements.txt
python extractor.py samples/invoice1.txt

# Task 2
cd task_2_rag_assistant
pip install -r requirements.txt
python app.py "Why did Kaikeyi ask for two boons?"
```

Both tasks need a free Gemini API key from [Google AI Studio](https://aistudio.google.com/). Copy `.env.example` to `.env` in the task folder and set `GEMINI_API_KEY`. The `.env` file is git-ignored and never committed.

## Notes

- **Task 2's PDF is not in this repo.** The demo book is copyrighted so put your own PDF in `task_2_rag_assistant/data/` and update `PDF_PATH` in `ingest.py`. The Task 2 README explains which settings are specific to the demo book.
- **Task 4** builds on Task 2 (a Streamlit chat UI over the same retrieval pipeline) and is not started.
- On Windows, quote the Task 1 folder name in PowerShell (`cd "task_1_llm_pipeline_&_json_extractor"`), because it contains an `&`.