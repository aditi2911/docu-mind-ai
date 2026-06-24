from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from rag_engine import process_document, answer_question
from agents import run_agent
from database import SessionLocal, Document, User
from auth import hash_password, verify_password, create_access_token, get_user_from_token
import os

app = FastAPI(title="DocuMind AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class Question(BaseModel):
    filename: str
    question: str


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = get_user_from_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


@app.post("/auth/register")
def register(payload: RegisterRequest):
    db = SessionLocal()
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password)
    )
    db.add(user)
    db.commit()
    db.close()
    return {"message": "Registered successfully"}


@app.post("/auth/login")
def login(payload: LoginRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.email == payload.email).first()
    db.close()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/")
def home():
    return {"message": "DocuMind AI is running"}


@app.get("/warmup")
def warmup():
    try:
        from rag_engine import get_qdrant_client
        get_qdrant_client()
        return {"status": "warm", "qdrant": "connected"}
    except Exception as e:
        return {"status": "warming", "error": str(e)}


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    filepath = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(await file.read())

    result = process_document(filepath, file.filename)

    db = SessionLocal()
    existing = db.query(Document).filter(
        Document.filename == file.filename,
        Document.owner_id == current_user.id
    ).first()
    if not existing:
        new_doc = Document(
            filename=file.filename,
            chunk_count=result["chunk_count"],
            status="ready",
            owner_id=current_user.id
        )
        db.add(new_doc)
        db.commit()
    db.close()

    return {
        "filename": file.filename,
        "chunks_created": result["chunk_count"],
        "status": "ready"
    }


@app.post("/ask")
def ask(
    payload: Question,
    current_user: User = Depends(get_current_user)
):
    result = run_agent(payload.question, payload.filename)
    return result


@app.get("/warmup")
async def warmup():
    import asyncio
    import httpx
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            resp = await client.get("https://docu-mind-qdrant.onrender.com/collections")
            return {"status": "warm", "qdrant": resp.status_code == 200}
    except Exception as e:
        return {"status": "warming", "error": str(e)}