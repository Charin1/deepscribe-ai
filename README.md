# DeepScribe AI

**Autonomous Agentic Blogging Platform** powered by LangChain + Groq with human-in-the-loop checkpoints.


![Python](https://img.shields.io/badge/python-3.11+-blue)
![React](https://img.shields.io/badge/react-18+-blue)

## 🌟 Features

- **🤖 AI Agent Pipeline** - Specialized agents (Title Strategist, Content Planner, Researcher, Writer, Editor)
- **🔍 Deep Research** - Automated web research with source credibility scoring
- **✨ Quality Content** - High-quality, human-like writing optimized for readability
- **👤 Human-in-the-Loop** - Control at every step (titles, outlines, drafts)
- **⚡ Real-time Updates** - WebSocket-powered live agent dashboard
- **📊 SEO Optimized** - Titles, structure, and metadata optimization

## 🏗️ Architecture

```
┌──────────────┐
│   React UI   │  ← Vite + TypeScript + TailwindCSS
└──────┬───────┘
       │ REST / WebSocket
┌──────▼────────┐
│  FastAPI API  │  ← Async Python + SQLAlchemy
└──────┬────────┘
       │
┌──────▼───────────────────────────┐
│ Agent Orchestration (LangChain)  │
├───────┬───────┬──────────────────┤
│ Title │Planner│ Research         │
│ Agent │ Agent │ Agents           │
├───────┼───────┼──────────────────┤
│ Writer│Insight│ Editor           │
│ Agent │ Agent │ Agent            │
└───────┴───────┴──────────────────┘
       │
┌──────▼────────────┐
│ - Groq LLM        │
│ - PostgreSQL      │
│ - Redis           │
└───────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for databases)
- Groq API key

### 1. Clone and Setup

```bash
cd deepscribe-ai

# Copy environment file
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 2. Start Databases

```bash
docker-compose up -d
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e .

# Run server
uvicorn app.main:app --reload
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

### 5. Open the App

Visit [http://localhost:5173](http://localhost:5173)

## 📁 Project Structure

```
deepscribe-ai/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI endpoints
│   │   ├── agents/       # LangChain agents
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # Business logic
│   │   ├── core/         # Config, database
│   │   └── main.py       # Entry point
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── pages/        # React pages
│   │   ├── components/   # UI components
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # API client
│   │   └── types/        # TypeScript types
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key (uses `openai/gpt-oss-120b`) | Yes |
| `DATABASE_URL` | PostgreSQL connection | Yes |
| `REDIS_URL` | Redis connection | Yes |
| `SERPER_API_KEY` | Serper search API | No |

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/projects` | Create project |
| POST | `/api/projects/{id}/generate-titles` | Generate titles |
| POST | `/api/projects/{id}/select-title` | Select title |
| POST | `/api/projects/{id}/generate-plan` | Generate outline |
| POST | `/api/projects/{id}/approve-plan` | Approve & start |
| GET | `/api/projects/{id}/status` | Execution status |
| GET | `/api/projects/{id}/result` | Get draft |
| POST | `/api/projects/{id}/export` | Export content |

## 🤝 Human-in-the-Loop Checkpoints

1. **Title Selection** - Choose from AI-generated SEO titles
2. **Plan Review** - Edit and lock outline sections
3. **Draft Review** - Approve or request rewrites
4. **Final Export** - Download in Markdown/HTML/WordPress
