"""Streamlit chat UI over the Task 2 RAG pipeline with streaming and chat memory."""

import sys
from pathlib import Path

import streamlit as st
from google.genai import errors

# Reuse the Task 2 modules instead of copying them.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "task_2_rag_assistant"))

from rag import TOP_K, build_prompt, finalize, get_client, stream_generate  # noqa: E402
from vector_store import CHROMA_DIR, build_index, load_index  # noqa: E402

HISTORY_TURNS = 6  # recent messages sent to the model as conversation memory

st.set_page_config(page_title="Document Q&A", page_icon="📖")
st.title("📖 Ask the document")
st.caption("Answers come only from the indexed PDF and cite the page.")


@st.cache_resource(show_spinner="Loading index and model...")
def load_resources():
    store = load_index() if CHROMA_DIR.exists() else build_index()
    return store, get_client()


try:
    store, client = load_resources()
except RuntimeError as e:
    st.error(str(e))
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question := st.chat_input("Ask a question about the document"):
    history = st.session_state.messages[-HISTORY_TURNS:]
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    docs = store.similarity_search(question, k=TOP_K)
    prompt = build_prompt(question, docs, history)

    with st.chat_message("assistant"):
        try:
            streamed = st.write_stream(stream_generate(prompt, client))
        except errors.APIError as e:
            st.error(f"API error {e.code}. Please try again in a moment.")
            st.stop()
        result = finalize(streamed, docs)
        if result["pages"]:
            st.caption("Sources: page " + ", ".join(str(p) for p in result["pages"]))

    reply = result["answer"]
    if result["pages"]:
        reply += "\n\n*Sources: page " + ", ".join(str(p) for p in result["pages"]) + "*"
    st.session_state.messages.append({"role": "assistant", "content": reply})