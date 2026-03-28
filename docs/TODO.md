# ProcureIQ — Master TODO List

Ordered by priority. Work top-to-bottom.

---

## 🔴 CRITICAL — Do before anything else

- [ ] **Get TinyFish API key** and confirm the exact API shape (endpoint, headers, request/response format)
  - Update `backend/services/tinyfish_client.py` accordingly
  - The `create_agent_task()` and `poll_task()` methods have TODO comments — fill these in
  
- [ ] **Get OpenAI API key** (or confirm using another LLM)

- [ ] **Copy `.env.example` to `.env`** and fill in all values

- [ ] **Test TinyFish with ONE supplier manually**
  - Run `backend/tests/test_agent.py --integration`
  - Confirm you get HTML back from a real site
  - Pick your 3 demo supplier URLs based on what actually works

- [ ] **Pick and lock your demo product query**
  - Test it on all 3 suppliers manually in a browser first
  - Confirm the product appears in search results
  - Confirm pricing is visible without login
  - Suggested: `"A4 copy paper 80gsm 500 sheets"` (universally available)

---

## 🟠 HIGH — Core features (Hours 0–12)

### Backend

- [ ] Run `pip install -r requirements.txt`
- [ ] Run `python seed.py` — confirm suppliers and demo jobs appear in DB
- [ ] Start server: `uvicorn main:app --reload`
- [ ] Test health: `curl http://localhost:8000/health`
- [ ] Test quote creation: `POST /api/quotes` with demo query
- [ ] Confirm background task fires and results appear in DB
- [ ] Test CSV export endpoint
- [ ] Test RFQ email endpoint

### Frontend

- [ ] Run `npm install` in `/frontend`
- [ ] Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local`
- [ ] Run `npm run dev` — confirm all 5 pages load without errors
- [ ] Wire New Quote form → submit → redirect to results page
- [ ] Confirm results page polls and updates cards
- [ ] Confirm staggered card reveal works (2.5s delay between cards)
- [ ] Test full happy path end-to-end at least 3 times

---

## 🟡 MEDIUM — Demo polish (Hours 12–20)

### Must-have visual elements

- [ ] Agent monologue typewriter animates while agents run
- [ ] Time saved counter updates every second
- [ ] Progress bar fills smoothly as results come in
- [ ] "RECOMMENDED" green ribbon on winner card
- [ ] RFQ modal opens, shows email, copy button works
- [ ] Toast notification fires when job completes

### Nice-to-have

- [ ] "You just saved X hours" toast on completion
- [ ] Live activity feed shows real agent steps (not just monologue)
- [ ] Parsed query banner shows before results
- [ ] Winner explanation bullets appear in sidebar
- [ ] Dashboard stat cards show real numbers from seeded data

---

## 🟢 LOW — If time allows (Hours 20+)

- [ ] Landing page hero section polished
- [ ] Mobile viewport tested and not broken
- [ ] Favicon set (ProcureIQ logo)
- [ ] Page titles correct in all tabs
- [ ] Supplier trust scores show in supplier library
- [ ] Alternative product suggestions from LLM

---

## 🚀 Deployment (Hour 22)

- [ ] Railway backend deployed and health check passing
- [ ] Railway frontend deployed and loading
- [ ] CORS_ORIGINS updated with production frontend URL
- [ ] Test full flow on deployed URL from a different device
- [ ] Test on mobile hotspot (not just your local WiFi)
- [ ] Get backup ngrok URL ready just in case

---

## 🎬 Demo Prep (Hour 23)

- [ ] Run demo query 10 times on prod. Confirm 8/10 succeed.
- [ ] Set DEMO_MODE=false on Railway (live agents)
- [ ] Seed prod DB with demo data: `python seed.py` on prod
- [ ] Record a perfect screen recording → save to Desktop as `procureiq_demo_backup.mp4`
- [ ] Have 2 backup product queries ready if primary fails
- [ ] Confirm pitch deck is 8 slides max, on screen, not in Drive

---

## 📋 Submission Checklist

- [ ] GitHub repo is public
- [ ] README has clear setup instructions
- [ ] `.env.example` committed (not `.env`)
- [ ] Deployed URL works and is in submission form
- [ ] Demo video recorded (60-90 seconds)
- [ ] Pitch deck uploaded
- [ ] Team member names correct in submission

---

## 🐛 Known Issues / Risks

| Risk | Mitigation |
|------|------------|

| TinyFish API shape unknown | Fill in `tinyfish_client.py` once you read the actual API docs |
| Supplier sites block agents | Pre-test all 3 suppliers; have DEMO_MODE as backup |
| LLM returns malformed JSON | All extractions wrapped in try/except with fallback |
| SQLite concurrency | asyncio.Lock in place; WAL mode enabled |
| Railway timeout | Uvicorn timeout set to 120s; agent timeout is 45s |
| Demo product not found | Use universally available product (A4 paper, USB cable) |

---

## 📞 If Something Breaks During Demo

1. **Agent returns empty/wrong data** → Switch `DEMO_MODE=true` on Railway → re-run query
2. **Railway is down** → `ngrok http 8000` from laptop → update frontend URL
3. **Frontend crashes** → Navigate judges to the deployed backend `/docs` and show API directly
4. **Total failure** → Play the screen recording backup from Desktop
5. **Never say "it was working this morning"** → Say "let me show you the recorded demo"
