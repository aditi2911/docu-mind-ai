# 📄 DocuMind AI

**Agentic RAG-powered document Q&A system** — upload a PDF, ask questions in natural language, get answers grounded strictly in the document content, with built-in hallucination detection.

> Status: Active development. Core backend (RAG + agents + vector DB) is complete and functional. Auth, Docker, and cloud deployment in progress.

## What it does

DocuMind AI lets you upload a document and ask questions about it. Instead of a single LLM call stuffing the whole document into a prompt, it uses a **multi-agent pipeline** built with LangGraph:

1. **Retriever Agent** — embeds the question and searches a Qdrant vector database for the most semantically relevant chunks of the document
2. **Reasoning Agent** — generates an answer using *only* the retrieved context
3. **Critic Agent** — independently fact-checks the generated answer against the retrieved context; if it isn't properly grounded, the system automatically retries retrieval (capped at 2 attempts) instead of returning an unverified answer

If the document doesn't contain the answer, the system explicitly says so rather than hallucinating.

## Architecture
Frontend (HTML/JS)

│

▼

FastAPI Backend

│

├──> PDF Upload → Chunking → Gemini Embeddings → Qdrant (vector DB)

│

├──> PostgreSQL (document metadata: filename, chunk count, status)

│

└──> LangGraph Agent Pipeline

Retriever → Reasoning → Critic

↑___________│

(retry loop, max 2 attempts)

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| LLM | Google Gemini (`gemini-2.5-flash-lite` for generation, `gemini-embedding-001` for embeddings) |
| Agent Orchestration | LangGraph |
| Vector Database | Qdrant |
| Relational Database | PostgreSQL + SQLAlchemy |
| Frontend | HTML / CSS / vanilla JS |
| PDF Processing | pypdf |

## Features

- PDF upload with automatic text extraction, chunking, and embedding
- Semantic (meaning-based) search over document content via Qdrant
- Multi-agent answer generation with self-verification (Critic agent)
- Hallucination resistance — explicitly refuses to answer when context is insufficient
- Graceful degradation on LLM API failures/rate limits (no crashes, clear error messages)
- Document metadata tracking in PostgreSQL
- Simple web UI for upload + chat

## Running locally

### Prerequisites
- Python 3.12+
- Docker Desktop (for Qdrant)
- PostgreSQL installed locally
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

### Setup

```bash
git clone https://github.com/aditi2911/docu-mind-ai.git
cd docu-mind-ai
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

Create a `.env` file:
GEMINI_API_KEY=your_gemini_key

DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/docu_mind_ai

Start Qdrant:
```bash
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant
```

Create the Postgres database (via psql or pgAdmin):
```sql
CREATE DATABASE docu_mind_ai;
```

Initialize tables:
```bash
python database.py
```

Run the backend:
```bash
uvicorn main:app --reload
```

Run the frontend (separate terminal):
```bash
cd Frontend
python -m http.server 5500
```

Visit `http://localhost:5500` to use the app, or `http://127.0.0.1:8000/docs` for the interactive API documentation.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/upload` | Upload a PDF; extracts, chunks, embeds, and stores it in Qdrant |
| POST | `/ask` | Ask a question about an uploaded document; returns agent-generated, fact-checked answer |
| GET | `/documents` | List all uploaded documents with metadata |

## Roadmap

- [x] PDF ingestion + chunking + embedding pipeline
- [x] Vector search via Qdrant
- [x] PostgreSQL metadata layer
- [x] LangGraph multi-agent workflow with grounding verification
- [x] Basic web UI
- [ ] JWT authentication + per-user document isolation
- [ ] Docker Compose (full stack: backend + Qdrant + Postgres in one command)
- [ ] Cloud deployment (AWS/GCP)
- [ ] Action agents (export to Excel, email summaries)
- [ ] Multi-document cross-referencing
- [ ] Observability/monitoring (Langfuse)

## Why this project

Built to demonstrate practical, production-shaped GenAI engineering: not just calling an LLM API, but designing a system with proper retrieval, multi-agent reasoning, grounding verification, and graceful failure handling — the concerns that separate a prototype from something an engineering team could actually build on.

## Author

**Aditi Rajawat**
[LinkedIn](www.linkedin.com/in/aditi-rajawat-29a813390) · [Portfolio](https://aditiport.vercel.app/) · [GitHub](https://github.com/aditi2911)