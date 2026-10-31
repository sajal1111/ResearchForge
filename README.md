# ResearchForge

> Forge reliable research from the web using intelligent AI agents.

A production-ready full-stack application wrapping a multi-agent research pipeline.
Plan → Search → Rank → Scrape → Summarize → Write → Review.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Uvicorn, Pydantic v2 |
| Pipeline | LangChain, OpenRouter (writer), Mistral AI (planner/summarizer/critic) |
| Search | Tavily |
| Scraping | BeautifulSoup4, Requests |
| Observability | LangSmith (optional) |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS v4 |

---

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # fill in your API keys
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

- App: http://localhost:5173

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | ✅ | Writer LLM (gpt-oss-120b via openrouter.ai) |
| `MISTRAL_API_KEY` | ✅ | Planner, summarizer, critic (mistral-small-2506) |
| `TAVILY_API_KEY` | ✅ | Web search |
| `ALLOWED_ORIGINS` | ✅ | Comma-separated CORS origins (e.g. `http://localhost:5173`) |
| `DEBUG` | ❌ | `true` to expose error details in 500 responses |
| `LANGSMITH_API_KEY` | ❌ | Enable LangSmith tracing (get key at smith.langchain.com) |
| `LANGSMITH_TRACING` | ❌ | Set to `true` to enable tracing |
| `LANGSMITH_PROJECT` | ❌ | LangSmith project name (default: `ResearchForge`) |

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_BASE_URL` | ✅ | Backend URL, e.g. `http://localhost:8000` |

---

## LangSmith Tracing

When `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` are set:

- Every LangChain chain call (planner, summarizer ×N, writer, critic) is automatically traced.
- Each API request is grouped under a single parent trace named `ResearchForge.run_research_pipeline`.
- Tags: `project=ResearchForge`, `provider=openrouter`, `provider=mistralai`, `model=gpt-oss-120b`, `model=mistral-small-2506`, `report_mode=<mode>`.
- When disabled (default), the app behaves exactly as without langsmith.

---

## Deployment

### Backend → Render / Railway

| Setting | Value |
|---------|-------|
| Root directory | `backend` |
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health check | `/health` |

Set all env vars from the table above in the Render dashboard.  
After deploying the frontend, add the Vercel URL to `ALLOWED_ORIGINS`.

### Frontend → Vercel

| Setting | Value |
|---------|-------|
| Framework preset | Vite |
| Root directory | `frontend` |
| Build command | `npm run build` |
| Output directory | `dist` |

Set `VITE_API_BASE_URL=https://your-backend.onrender.com` in Vercel environment variables.

---

## Report Modes

| Mode | Length | Focus |
|------|--------|-------|
| `quick_summary` | 150–250 words | Key takeaways only |
| `deep_research` | 500–800 words | Thorough, well-sourced |
| `technical` | 400–700 words | Engineering audience |
| `business` | 400–700 words | Decision-makers |
| `interview_prep` | 300–600 words | Q&A pairs + key facts |
