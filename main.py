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
    try:
        result = run_agent(payload.question, payload.filename)
        return result
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
def list_documents(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    docs = db.query(Document).filter(Document.owner_id == current_user.id).all()
    db.close()
    return [
        {
            "filename": d.filename,
            "chunk_count": d.chunk_count,
            "status": d.status,
            "uploaded_at": str(d.uploaded_at)
        }
        for d in docs
    ]


@app.get("/debug/chunks")
def debug_chunks(current_user: User = Depends(get_current_user)):
    from rag_engine import get_qdrant_client, COLLECTION_NAME
    qdrant = get_qdrant_client()
    results = qdrant.scroll(
        collection_name=COLLECTION_NAME,
        limit=10,
        with_payload=True,
        with_vectors=False
    )
    filenames = list(set([p.payload.get("filename") for p in results[0]]))
    return {"stored_filenames": filenames}

@app.get("/debug/search/{filename}")
def debug_search(filename: str, current_user: User = Depends(get_current_user)):
    from rag_engine import get_qdrant_client, COLLECTION_NAME, get_embedding
    qdrant = get_qdrant_client()
    q_embedding = get_embedding("What is this person's name?")
    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=q_embedding,
        query_filter={
            "must": [{"key": "filename", "match": {"value": filename}}]
        },
        limit=3
    )
    unfiltered = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=q_embedding,
        limit=3
    )
    return {
        "filtered_results": len(results.points),
        "unfiltered_results": len(unfiltered.points),
        "filtered_payloads": [p.payload for p in results.points],
        "unfiltered_payloads": [p.payload.get("filename") for p in unfiltered.points]
    }