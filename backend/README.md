# ProcureIQ — Backend

FastAPI backend with TinyFish agent orchestration.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
# Fill in TINYFISH_API_KEY and OPENAI_API_KEY

python seed.py          # seed DB with suppliers + demo data
uvicorn main:app --reload --port 8000
```

## API Docs

- Swagger UI: <http://localhost:8000/docs>
- ReDoc:       <http://localhost:8000/redoc>

## Key Files

| File | Purpose |
|------|---------|

| `main.py` | FastAPI app, CORS, router registration |
| `services/agent_orchestrator.py` | Parallel TinyFish task management |
| `services/tinyfish_client.py` | TinyFish API wrapper — **update with real API shape** |
| `services/extraction_service.py` | LLM HTML → structured JSON |
| `services/comparison_engine.py` | Scoring, tagging, winner selection |
| `seed.py` | DB seeding for demo data |

## TODOs Before Hackathon Demo

- [ ] Confirm TinyFish API request/response shape (see `tinyfish_client.py` TODOs)
- [ ] Test all 3 demo supplier URLs with your exact demo product query
- [ ] Set `DEMO_MODE=false` for live demo, `true` as fallback
- [ ] Verify Railway health check passes: `curl https://your-app.railway.app/health`
- [ ] Run `python seed.py` on production DB to populate demo data

## Environment Variables

See `../.env.example` for full list.

## Testing

```bash
# Unit tests
pytest tests/ -v

# Integration test (requires API keys)
pytest tests/test_agent.py -v --integration
```
