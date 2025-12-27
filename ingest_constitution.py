import os
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI
from pypdf import PdfReader
import uuid

load_dotenv()

EMBED_MODEL = "text-embedding-3-small"
PINECONE_INDEX_NAME = os.environ["PINECONE_INDEX_NAME"]

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(PINECONE_INDEX_NAME)
client = OpenAI()

def load_pdf(path):
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n".join(parts)

def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def embed_chunks(chunks, batch_size=64):
    vectors = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=batch,
        )
        for j, record in enumerate(response.data):
            vectors.append(
                {
                    "id": str(uuid.uuid4()),
                    "values": record.embedding,
                    "metadata": {"text": batch[j]},
                }
            )
    return vectors

def upsert_vectors(vectors, batch_size=100):
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)

def main():
    pdf_path = os.environ.get("CONSTITUTION_PDF_PATH", "constitution.pdf")
    text = load_pdf(pdf_path)
    chunks = chunk_text(text)
    vectors = embed_chunks(chunks)
    upsert_vectors(vectors)
    print("Ingestion complete. Total chunks:", len(chunks))

if __name__ == "__main__":
    main()