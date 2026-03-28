# 🔍 ProcureIQ

> **Autonomous B2B Multi-Vendor Quote Collection — Powered by TinyFish Web Agent API**

Drop in a product description. Get back real supplier quotes from live websites in under 90 seconds. No APIs. No databases. A real browser agent doing real procurement work.

---

## 📦 What's Inside

```
procureiq/
├── backend/          # FastAPI Python backend + TinyFish agent orchestration
├── frontend/         # Next.js 14 + Tailwind CSS + shadcn/ui
├── docs/             # Architecture, API reference, deployment guides
├── .env.example      # All required environment variables
└── docker-compose.yml
```

---

## ⚡ Quick Start (5 Minutes)

### Prerequisites

- Python 3.11+
- Node.js 18+
- TinyFish API key → [tinyfish.io](https://tinyfish.io)
- OpenAI API key (for extraction + RFQ generation)

### 1. Clone & Configure

```bash
git clone https://github.com/yourteam/procureiq.git
cd procureiq
cp .env.example .env
# Fill in your API keys in .env
```

### 2. Start Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py                  # Seeds DB with demo data + default suppliers
uvicorn main:app --reload --port 8000
```

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:3000
```

### 4. Verify Everything Works

```bash
curl http://localhost:8000/health
# → {"status":"ok","version":"1.0.0","db":"connected"}
```

Open <http://localhost:3000> → click "New Quote Hunt" → try:
> `"500 units M8 zinc-plated hex bolts grade 8.8"`

---

## 🏗️ Architecture Overview

```
User → Next.js Frontend
         ↓ POST /api/quotes
       FastAPI Backend
         ↓ asyncio.gather (3 parallel)
       TinyFish Agent (×3)
         ↓ navigates real websites
       Raw HTML
         ↓ OpenAI GPT-4o mini
       Structured Quote JSON
         ↓ Comparison Engine
       Ranked Results + Winner
         ↓ SSE / Polling
       Frontend Results Page
```

---

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|

| `TINYFISH_API_KEY` | Your TinyFish API key | ✅ |
| `OPENAI_API_KEY` | OpenAI key for extraction + RFQ | ✅ |
| `DATABASE_URL` | SQLite path (default: `./procureiq.db`) | ✅ |
| `DEMO_MODE` | `true` = use cached results, skip live agents | Optional |
| `CORS_ORIGINS` | Allowed frontend origins | ✅ |
| `SECRET_KEY` | App secret for future auth | ✅ |

---

## 🚀 Deployment (Railway)

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for step-by-step Railway deploy.

TL;DR:

```bash
railway login
railway init
railway up
```

---

## 📋 Demo Checklist

Run this before every demo:

- [ ] Backend health check returns `"status":"ok"`
- [ ] Demo query tested successfully in last 2 hours
- [ ] Screen recording saved to Desktop as backup
- [ ] DEMO_MODE=false (live agents, not cached)
- [ ] DB seeded with 5 historical quotes (looks like real usage)
- [ ] All 3 supplier URLs tested and returning data
- [ ] Frontend deployed URL works on mobile viewport

---

## 🗺️ Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for full post-hackathon plan.

---

## 🤝 Built With

- [TinyFish](https://tinyfish.io) — Autonomous web agent infrastructure
- [FastAPI](https://fastapi.tiangolo.com) — Python backend
- [Next.js 14](https://nextjs.org) — React frontend
- [shadcn/ui](https://ui.shadcn.com) — Component library
- [OpenAI GPT-4o mini](https://openai.com) — Structured data extraction

---

## 📄 License

MIT — built at TinyFish $2M Pre-Accelerator Hackathon
