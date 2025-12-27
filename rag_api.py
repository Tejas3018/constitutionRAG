from fastapi import FastAPI
from pydantic import BaseModel
from chat_constitution import answer_question

app = FastAPI(title="Constitution RAG API")

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    answer = answer_question(req.question)
    return {"answer": answer}