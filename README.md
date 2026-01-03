# Constitution RAG API

A small Retrieval-Augmented Generation (RAG) service that answers questions about a Constitution PDF using:

- **OpenAI** for embeddings and chat
- **Pinecone** for vector search
- **FastAPI + Uvicorn** for the HTTP API

 deployed URL: `https://constitutionrag.onrender.com/chat`

---

## Overview

**Ingestion (`ingest_constitution.py`)**

1. Load `constitution.pdf`.
2. Extract text with `pypdf`.
3. Chunk text into overlapping segments.
4. Generate embeddings with OpenAI (`text-embedding-3-small`, 1536 dims).
5. Upsert vectors into a Pinecone index (e.g. `constitution-index`) with the chunk text in metadata.

**Query / API (`chat_constitution.py`, `rag_api.py`)**

1. Take a user question.
2. Embed the question with the same OpenAI embedding model.
3. Query Pinecone for the most similar chunks.
4. Build a context string from the retrieved chunks.
5. Call an OpenAI chat model (e.g. `gpt-4.1-mini`) with the context + question.
6. Return the answer as JSON.

---

## Project Structure

```text
chat_constitution.py   # RAG query logic (search + OpenAI chat)
ingest_constitution.py # One-time ingestion script for the PDF
rag_api.py             # FastAPI app exposing POST /chat
constitution.pdf       # Source document
requirements.txt       # Python dependencies
.gitignore             # Ignore .env, .venv, etc.
```

---

