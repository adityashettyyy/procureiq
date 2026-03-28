# ProcureIQ — Deployment Guide

## Railway (Recommended for Hackathon)

### Backend

```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. From /backend directory
cd backend
railway init          # creates new project
railway up            # deploys

# 4. Set environment variables in Railway dashboard:
#    TINYFISH_API_KEY=xxx
#    OPENAI_API_KEY=xxx
#    CORS_ORIGINS=https://your-frontend.railway.app
#    DEMO_MODE=false

# 5. Get your backend URL:
#    https://procureiq-backend.railway.app
```

### Frontend

```bash
# From /frontend directory
cd frontend
railway init          # new service in same project
# Set env var: NEXT_PUBLIC_API_URL=https://procureiq-backend.railway.app
railway up
```

### railway.toml (backend)

```toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "python seed.py && uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 30
```

### railway.toml (frontend)

```toml
[build]
builder = "NIXPACKS"
buildCommand = "npm install && npm run build"

[deploy]
startCommand = "npm start"
```

---

## Render (Alternative)

```bash
# render.yaml at project root
services:
  - type: web
    name: procureiq-backend
    runtime: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && python seed.py && uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: TINYFISH_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false

  - type: web
    name: procureiq-frontend
    runtime: node
    buildCommand: cd frontend && npm install && npm run build
    startCommand: cd frontend && npm start
```

---

## Local Docker (Optional)

```bash
# From project root
docker-compose up --build
# Backend:  http://localhost:8000
# Frontend: http://localhost:3000
```

---

## Pre-Deploy Checklist

```
□ TINYFISH_API_KEY set and valid
□ OPENAI_API_KEY set and valid
□ CORS_ORIGINS includes deployed frontend URL
□ DATABASE_URL set (Railway auto-provides Postgres URL if you add plugin)
□ DEMO_MODE=false for live demo
□ Health check passes: curl https://your-backend.railway.app/health
□ Seed ran: python seed.py (or runs on startup via main.py lifespan)
□ Frontend .env.local has correct NEXT_PUBLIC_API_URL
□ Tested from mobile viewport
□ Screen recording saved as backup
```

---

## Ngrok Fallback (Emergency)

If Railway is down during judging:

```bash
# Terminal 1 — start backend locally
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2 — expose backend
ngrok http 8000
# → Copy the https://xxxxx.ngrok.io URL

# Terminal 3 — update frontend .env.local
NEXT_PUBLIC_API_URL=https://xxxxx.ngrok.io
npm run dev
# → http://localhost:3000
```

This works from any wifi network including a phone hotspot.
