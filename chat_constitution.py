import os
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI

load_dotenv()

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4.1-mini"
PINECONE_INDEX_NAME = os.environ["PINECONE_INDEX_NAME"]

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(PINECONE_INDEX_NAME)
client = OpenAI()

def get_embedding(text):
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=[text],
    )
    return response.data[0].embedding

def search_index(query, top_k=5):
    vector = get_embedding(query)
    response = index.query(
        vector=vector,
        top_k=top_k,
        include_metadata=True,
    )
    if isinstance(response, dict):
        return response.get("matches", [])
    return response.matches

def build_context(matches):
    parts = []
    for m in matches:
        metadata = m["metadata"] if isinstance(m, dict) else m.metadata
        text = metadata.get("text")
        if text:
            parts.append(text)
    return "\n\n---\n\n".join(parts)

def answer_question(question):
    matches = search_index(question)
    context = build_context(matches)
    system_prompt = (
        "You are a helpful assistant that answers questions about the Constitution. "
        "Use only the information from the provided context when possible. "
        "If the answer is not in the context, say that you do not know based on the document."
    )
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}",
            },
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content

def main():
    while True:
        question = input("Ask a question about the Constitution (or 'exit'): ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        answer = answer_question(question)
        print("\nAnswer:\n")
        print(answer)
        print("\n")

if __name__ == "__main__":
    main()