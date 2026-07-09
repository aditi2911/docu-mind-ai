<div align="center">

# 📄 DocuMind AI

### *Ask anything. Across any document. With agents that verify their own answers.*

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Visit_App-4f7cff?style=for-the-badge)](https://docu-mind-ai-lik6.vercel.app)
[![API Docs](https://img.shields.io/badge/📡_API_Docs-Swagger_UI-green?style=for-the-badge)](https://docu-mind-backend-g4gz.onrender.com/docs)
[![GitHub](https://img.shields.io/badge/🐙_GitHub-View_Code-black?style=for-the-badge)](https://github.com/aditi2911/docu-mind-ai)

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.138-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange)
![Qdrant](https://img.shields.io/badge/Qdrant-Cloud-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Render-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

</div>

---

## 🎯 What makes this different from every other "chat with PDF" project?

Most RAG demos do this:
```
Question → LLM → Answer  ❌ (can hallucinate)
```

DocuMind AI does this:
```
Question → Retrieve → Reason → Critic verifies → Answer  ✅ (grounded)
         ↑___________________________|
              (auto-retries if ungrounded)
```

A **Critic Agent** independently fact-checks every answer against the retrieved context before it reaches the user. If the answer isn't grounded, it retries. If the document doesn't contain the answer, it says so — it never makes things up.

---

## 🏗️ Architecture

```mermaid
graph TD
    A[🌐 Next.js Frontend<br/>Vercel] -->|JWT + HTTPS| B[⚡ FastAPI Backend<br/>Render]
    
    B --> C[📦 PDF Ingestion<br/>Chunking + Embeddings]
    C --> D[🗄️ Qdrant Cloud<br/>Vector Database]
    B --> F[🐘 PostgreSQL<br/>Users + Documents]
    
    B --> G[🤖 LangGraph<br/>Agent Orchestrator]
    G --> H[🔍 Retriever Agent<br/>Semantic Search]
    H --> I[🧠 Reasoning Agent<br/>Gemini 2.5]
    I --> J{⚖️ Critic Agent<br/>Fact-Check}
    J -->|Not grounded — retry| H
    J -->|Grounded ✓| K[✅ Verified Response]

    style A fill:#4f7cff,color:#fff,stroke:#3a63e0
    style B fill:#1a1d27,color:#e6e6e6,stroke:#4f7cff
    style G fill:#2d1a47,color:#e6e6e6,stroke:#8b5cf6
    style J fill:#1a2d1a,color:#e6e6e6,stroke:#4ade80
    style K fill:#4ade80,color:#000,stroke:#22c55e
    style D fill:#dc2626,color:#fff,stroke:#b91c1c
    style F fill:#336791,color:#fff,stroke:#1e40af
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Semantic Search** | Finds relevant content by meaning, not keywords — using Gemini embeddings + Qdrant vector similarity |
| 🤖 **Multi-Agent Grounding** | 3-agent LangGraph pipeline: Retrieve → Reason → Critic. Hallucination-resistant by design |
| 🔐 **JWT Authentication** | Secure register/login with bcrypt hashing. Per-user document isolation |
| 📤 **PDF Upload & Indexing** | Automatic text extraction, chunking, embedding, and storage in Qdrant Cloud |
| 💬 **Next.js Chat UI** | Clean React frontend with auth, document dashboard, and per-document chat pages |
| 📊 **Document Management** | Upload history, chunk counts, and status tracking in PostgreSQL |
| 🐳 **Docker Compose** | Full local stack (backend + Qdrant + Postgres) with a single command |
| ☁️ **Cloud Deployed** | Live on Render (backend) + Vercel (frontend) + Qdrant Cloud (vectors) |

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | Next.js 16 + Tailwind CSS | React-based, deployed on Vercel with zero config |
| Backend API | FastAPI (Python 3.12) | Auto-generates Swagger docs, async support, Pydantic validation |
| Agent Orchestration | LangGraph | Stateful graph with conditional edges — enables retry loops |
| LLM + Embeddings | Google Gemini 2.5 + gemini-embedding-001 | Free tier, 3072-dim embeddings, fast generation |
| Vector Database | Qdrant Cloud | Persistent, always-on, keyword payload filtering |
| Relational DB | PostgreSQL (Render managed) | User management, document metadata, upload history |
| Auth | JWT + bcrypt | Stateless auth, secure password hashing |
| Local Dev | Docker Compose | One command to spin up full stack locally |
| CI/CD | GitHub → Render + Vercel auto-deploy | Every push to main triggers automatic deployment |

---

## 📡 API Reference

```
POST   /auth/register      Register a new user
POST   /auth/login         Login → returns JWT token
POST   /upload    🔒       Upload PDF → chunk → embed → store in Qdrant
POST   /ask       🔒       Multi-agent Q&A with grounding verification
GET    /documents  🔒      List all uploaded documents with metadata
GET    /warmup             Health check + Qdrant connection warm-up
```

🔒 = Requires `Authorization: Bearer <token>` header

**Example `/ask` response:**
```json
{
  "answer": "Associate — Human Resource Operations at Wipro HR Services India Ltd.",
  "is_grounded": true,
  "attempts": 1
}
```

---

## 🚀 Running Locally

**Prerequisites:** Python 3.12+, Docker Desktop, [Gemini API key](https://aistudio.google.com/apikey) (free)

```bash
# 1. Clone the repo
git clone https://github.com/aditi2911/docu-mind-ai.git
cd docu-mind-ai

# 2. Set up Python environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt

# 3. Create .env file
GEMINI_API_KEY=your_key_here
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/docu_mind_ai

# 4. Start full stack (backend + Qdrant + Postgres)
docker-compose up --build

# 5. Run Next.js frontend (new terminal)
cd frontend-next
npm install
npm run dev
```

| Service | URL |
|---|---|
| API Docs (Swagger) | http://localhost:8000/docs |
| Next.js Frontend | http://localhost:3000 |
| Qdrant Dashboard | http://localhost:6333/dashboard |

---

## 📁 Project Structure

```
docu-mind-ai/
│
├── 🐍 main.py              FastAPI app — all API endpoints
├── 🧠 rag_engine.py        PDF processing, embeddings, Qdrant search
├── 🤖 agents.py            LangGraph multi-agent pipeline
├── 🔐 auth.py              JWT auth + bcrypt password hashing
├── 🗄️  database.py          SQLAlchemy models (User, Document)
│
├── ⚛️  frontend-next/       Next.js 16 frontend (deployed to Vercel)
│   └── app/
│       ├── page.tsx        Login / Register
│       ├── dashboard/      Document upload + management
│       └── chat/[filename] Chat interface per document
│
├── 🐳 Dockerfile           Container config for backend
├── 🐳 docker-compose.yml   Local full-stack setup
└── 📋 requirements.txt     Python dependencies
```

---

## 🗺️ Roadmap

- [x] PDF ingestion pipeline (extract → chunk → embed → store)
- [x] Qdrant Cloud vector search with payload filtering
- [x] LangGraph multi-agent (Retriever → Reasoning → Critic)
- [x] JWT authentication + per-user document isolation
- [x] Next.js frontend with auth, dashboard, and chat
- [x] Docker Compose for local development
- [x] Full cloud deployment (Render + Vercel + Qdrant Cloud)
- [ ] Action agents (export answers to Excel, email summaries)
- [ ] Multi-document cross-referencing
- [ ] Observability dashboard (Langfuse — token cost + latency tracking)
- [ ] Streaming responses via Server-Sent Events

---

## 💡 Engineering Decisions Worth Noting

**Why LangGraph over a simple chain?**
LangGraph supports conditional edges — the Critic can loop back to the Retriever if the answer isn't grounded. A simple sequential chain can't make that decision.

**Why Qdrant Cloud over self-hosted?**
Render's free tier has ephemeral storage — files disappear on redeploy. Qdrant Cloud persists data permanently and stays always-on (no cold start).

**How is hallucination prevented?**
Retrieved chunks are the *only* context passed to the model. The Reasoning Agent is instructed to say "I don't know" if the answer isn't there. The Critic then independently verifies — if not grounded, it retries retrieval up to 2 times.

---

## 🙋 Author

<div align="center">

**Aditi Rajawat**

*BCA (Hons) — ITM University Gwalior | CGPA: 8.4*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?logo=linkedin)](www.linkedin.com/in/aditi-rajawat-29a813390)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-4f7cff)](https://aditiport.vercel.app)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)](https://github.com/aditi2911)

</div>

---

<div align="center">
<i>Built from scratch — starting from zero Python experience.</i><br/>
<i>Every line of code here was written, debugged, and understood.</i>
</div>