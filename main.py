from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from rag_engine import process_document, answer_question
from database import SessionLocal, Document
import os

app = FastAPI(title="DocuMind AI")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development only — we'll restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Question(BaseModel):
    filename: str
    question: str


@app.get("/")
def home():
    return {"message": "DocuMind AI is running"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    filepath = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(await file.read())

    result = process_document(filepath, file.filename)

    db = SessionLocal()
    existing = db.query(Document).filter(Document.filename == file.filename).first()
    if not existing:
        new_doc = Document(
            filename=file.filename,
            chunk_count=result["chunk_count"],
            status="ready"
        )
        db.add(new_doc)
        db.commit()
    db.close()

    return {
        "filename": file.filename,
        "chunks_created": result["chunk_count"],
        "status": "ready"
    }


from agents import run_agent

@app.post("/ask")
def ask(payload: Question):
    result = run_agent(payload.question, payload.filename)
    return result

@app.get("/documents")
def list_documents():
    db = SessionLocal()
    docs = db.query(Document).all()
    db.close()
    return [
        {"filename": d.filename, "chunk_count": d.chunk_count, "status": d.status, "uploaded_at": d.uploaded_at}
        for d in docs
    ]