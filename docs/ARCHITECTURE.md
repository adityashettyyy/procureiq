# ProcureIQ — Architecture Document

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                         │
│                    Next.js 14 Frontend                      │
│         (Landing / Dashboard / New Quote / Results)         │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP (REST + CSV streaming)
                           │ polling every 2.5s
┌──────────────────────────▼──────────────────────────────────┐
│                    FastAPI Backend                           │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ /api/quotes │  │/api/suppliers│  │  /api/metrics    │   │
│  └──────┬──────┘  └──────────────┘  └──────────────────┘   │
│         │                                                   │
│  ┌──────▼──────────────────────────────────────────────┐   │
│  │            Agent Orchestrator                        │   │
│  │  asyncio.gather → 3 parallel TinyFish tasks          │   │
│  │  asyncio.Lock  → safe SQLite writes                  │   │
│  └──────┬──────────────────┬────────────────────┬──────┘   │
│         │                  │                    │           │
└─────────┼──────────────────┼────────────────────┼──────────┘
          │                  │                    │
┌─────────▼──────┐  ┌────────▼───────┐  ┌────────▼──────────┐
│  TinyFish API  │  │  TinyFish API  │  │  TinyFish API      │
│  Agent Task 1  │  │  Agent Task 2  │  │  Agent Task 3      │
│  (Supplier A)  │  │  (Supplier B)  │  │  (Supplier C)      │
└─────────┬──────┘  └────────┬───────┘  └────────┬──────────┘
          │                  │                    │
          └──────────────────┼────────────────────┘
                             │ Raw HTML
┌────────────────────────────▼────────────────────────────────┐
│                  OpenAI GPT-4o-mini                          │
│           HTML → Structured QuoteData JSON                   │
│           + Winner Explanation Bullets                       │
│           + RFQ Email Generation                             │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│              Comparison Engine (pure Python)                 │
│   Price 50% · Speed 30% · Availability 20%                  │
│   Tags: is_best_value · is_fastest · is_recommended         │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                   SQLite (WAL mode)                          │
│   quote_jobs · quote_results · suppliers · rfq_drafts        │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow (Single Quote Job)

```
1. POST /api/quotes
   ├── Parse product query (LLM call #1 — query reformulation)
   ├── Create QuoteJob (status=PENDING)
   └── Fire background task: orchestrate_quote_job()

2. orchestrate_quote_job() [background]
   ├── Update job status → RUNNING
   ├── asyncio.gather([agent_task_1, agent_task_2, agent_task_3])
   │
   │   Each agent_task:
   │   ├── Call TinyFish API → create browser agent task
   │   ├── Poll TinyFish until complete (every 2s, max 45s)
   │   ├── Receive raw HTML of product page
   │   ├── Call OpenAI extraction (LLM call #2)
   │   ├── Parse JSON → QuoteResult fields
   │   └── Write to DB (with asyncio.Lock)
   │
   ├── All tasks complete → compute_scores()
   ├── Tag: is_best_value, is_fastest, is_recommended
   ├── Call OpenAI for winner explanation (LLM call #3)
   └── Update QuoteJob → status=COMPLETE

3. Frontend polls GET /api/quotes/{id}/status every 2.5s
   ├── Receives per-result status
   └── Reveals cards with 2.5s stagger as each completes

4. User clicks "Get RFQ Email"
   ├── POST /api/quotes/{id}/rfq-email
   ├── LLM call #4 → formal RFQ email text
   └── Stored in rfq_drafts table
```

## Concurrency Model

- FastAPI runs with uvicorn in async mode
- All DB operations use SQLAlchemy async (aiosqlite)
- asyncio.Lock prevents concurrent SQLite writes
- SQLite WAL mode allows concurrent reads
- 3 agent tasks run in parallel via asyncio.gather
- Background tasks don't block the HTTP response

## Demo Mode Architecture

When `DEMO_MODE=true`:

- `_run_demo_mode()` is called instead of real agent tasks
- Returns hardcoded realistic data with simulated delays
- Identical DB writes and comparison logic as live mode
- Frontend sees no difference — same API, same polling

This is the reliability safety net for the live demo.

## LLM Call Budget (per quote job)

| Call | Purpose | Model | Est. tokens | Est. cost |
|------|---------|-------|-------------|-----------|

| #1 | Query parse | gpt-4o-mini | 200 | $0.00006 |
| #2 × 3 | HTML extraction | gpt-4o-mini | 2000 × 3 | $0.00054 |
| #3 | Winner explanation | gpt-4o-mini | 300 | $0.00009 |
| #4 | RFQ email | gpt-4o-mini | 600 | $0.00018 |
| **Total** | | | ~7000 | **~$0.001** |

Cost per quote job: ~$0.001 USD. Negligible.
