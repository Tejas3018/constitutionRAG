# Constitution RAG API

A small Retrieval-Augmented Generation (RAG) service that answers questions about a Constitution PDF using:

- **OpenAI** for embeddings and chat
- **Pinecone** for vector search
- **FastAPI + Uvicorn** for the HTTP API

Example deployed URL: `https://constitutionrag.onrender.com/chat`

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

## Setup

### 1. Clone and install

```bash
git clone https://github.com/Tejas3018/constitutionRAG.git
cd constitutionRAG

python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file (not committed):

```env
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=constitution-index
CONSTITUTION_PDF_PATH=./constitution.pdf
```

Create a Pinecone index:

- Type: Dense
- Dimension: `1536`
- Metric: cosine
- Name: `constitution-index` (or match `PINECONE_INDEX_NAME`)

---

## Ingest the Constitution

Run once (or whenever the PDF changes):

```bash
python ingest_constitution.py
```

This reads `constitution.pdf`, chunks it, embeds each chunk, and stores the vectors in Pinecone.

---

## Run the API locally

```bash
uvicorn rag_api:app --host 0.0.0.0 --port 8000
```

**Health check**

```bash
curl http://localhost:8000/
# -> {"status":"ok"}
```

**Query endpoint**

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the preamble say about justice?"}'
```

Response:

```json
{"answer": "..."}
```

---

## Deployment (Render)

1. Push this repo to GitHub.
2. On Render, create a **Web Service** from the repo.
3. Set:

   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn rag_api:app --host 0.0.0.0 --port $PORT`

4. Add environment variables in Render:

   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY`
   - `PINECONE_INDEX_NAME`

Once deployed, your public RAG endpoint will be:

```text
https://<your-render-name>.onrender.com/chat
```

This URL can be used by any frontend (e.g. Lovable) that sends:

```json
{ "question": "your question here" }
```

and expects:

```json
{ "answer": "..." }
```
