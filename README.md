# 📄 DocuMind AI
### Multi-Agent RAG-Powered Document Intelligence Platform

**🚀 Live Demo:** https://docu-mind-ai-six.vercel.app  
**📡 API Docs:** https://docu-mind-backend-g4gz.onrender.com/docs  
**🐙 GitHub:** https://github.com/aditi2911/docu-mind-ai

---

## What it does

Upload any PDF. Ask questions in plain English. Get answers grounded strictly in your document — with a built-in AI that verifies its own answers before returning them.

DocuMind AI is not a "chat with PDF" demo. It uses a **multi-agent pipeline** built with LangGraph where three specialized agents collaborate:

- **Retriever Agent** — embeds your question and searches Qdrant Cloud for the most semantically relevant document chunks
- **Reasoning Agent** — generates an answer using *only* the retrieved context, never its own memory
- **Critic Agent** — independently fact-checks the answer against the retrieved context; if ungrounded, triggers automatic re-retrieval (max 2 retries)

If the answer isn't in the document, the system says so — it doesn't hallucinate.

---

## Architecture

```mermaid
graph TD
    A[🌐 Vercel Frontend] -->|HTTPS requests| B[⚡ FastAPI Backend on Render]
    B --> C[📦 PDF Upload & Chunking]
    C --> D[🔢 Gemini Embeddings]
    D --> E[🗄️ Qdrant Cloud Vector DB]
    B --> F[🐘 PostgreSQL on Render]
    B --> G[🤖 LangGraph Agent Pipeline]
    G --> H[🔍 Retriever Agent]
    H --> I[🧠 Reasoning Agent]
    I --> J[⚖️ Critic Agent]
    J -->|Not grounded| H
    J -->|Grounded ✓| K[✅ Response to User]

    style A fill:#4f7cff,color:#fff
    style G fill:#1a1d27,color:#e6e6e6
    style J fill:#23314d,color:#e6e6e6
    style K fill:#4ade80,color:#000
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Vanilla JS — deployed on Vercel |
| Backend | FastAPI (Python 3.12) — deployed on Render |
| Agent Orchestration | LangGraph |
| LLM & Embeddings | Google Gemini (`gemini-2.5-flash-lite` + `gemini-embedding-001`) |
| Vector Database | Qdrant Cloud |
| Relational Database | PostgreSQL (Render managed) |
| Auth | JWT (python-jose + bcrypt) |
| PDF Processing | pypdf |
| Local Dev | Docker Compose (FastAPI + Qdrant + Postgres) |
| CI/CD | GitHub → auto-deploy on Render + Vercel |

---

## Key Features

- **Semantic search** — finds relevant chunks by meaning, not keywords
- **Multi-agent grounding** — Critic agent prevents hallucination
- **JWT authentication** — register, login, per-user document isolation
- **Production deployment** — live on cloud with real HTTPS URLs
- **Auto-generated API docs** — interactive Swagger UI at `/docs`
- **Docker Compose** — full local stack with one command

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Create account |
| POST | `/auth/login` | No | Get JWT token |
| POST | `/upload` | Yes | Upload + index PDF |
| POST | `/ask` | Yes | Agent-powered Q&A |
| GET | `/documents` | Yes | List uploaded docs |
| GET | `/warmup` | No | Wake services |

---

## Running Locally

### Prerequisites
- Python 3.12+
- Docker Desktop
- Free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

### Setup

```bash
git clone https://github.com/aditi2911/docu-mind-ai.git
cd docu-mind-ai

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

Create `.env`:
GEMINI_API_KEY=your_key_here
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/docu_mind_ai

Start full stack:
```bash
docker-compose up --build
```

Visit `http://localhost:8000/docs` for API or open `Frontend/index.html` for UI.

---

## Project Structure
docu-mind-ai/

├── main.py              # FastAPI app + all endpoints

├── rag_engine.py        # PDF processing, embeddings, Qdrant search

├── agents.py            # LangGraph multi-agent pipeline

├── auth.py              # JWT auth, password hashing

├── database.py          # SQLAlchemy models (User, Document)

├── Frontend/

│   └── index.html       # Chat UI (deployed on Vercel)

├── Dockerfile           # Container config

├── docker-compose.yml   # Local full-stack setup

└── requirements.txt

---

## Roadmap

- [x] PDF ingestion + chunking + semantic embeddings
- [x] Qdrant Cloud vector search
- [x] PostgreSQL metadata + user management
- [x] LangGraph multi-agent with grounding verification
- [x] JWT authentication + per-user document isolation
- [x] Frontend chat UI
- [x] Docker Compose local development
- [x] Cloud deployment (Render + Vercel + Qdrant Cloud)
- [ ] Action agents (export to Excel, email summaries)
- [ ] Multi-document cross-referencing
- [ ] Monitoring dashboard (Langfuse)
- [ ] Upgrade to Next.js frontend

---



## Author

**Aditi Rajawat**  
BCA (Hons) — ITM University Gwalior | CGPA 8.4  
[LinkedIn](https://linkedin.com/in/your-profile) · [Portfolio](https://aditiport.vercel.app) · [GitHub](https://github.com/aditi2911)