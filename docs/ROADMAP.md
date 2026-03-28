# ProcureIQ — Post-Hackathon Roadmap

## Immediate (Week 1–2)

### Hardening

- [ ] Replace SQLite with PostgreSQL (Railway plugin, one env var change)
- [ ] Add proper job queue (Celery + Redis or BullMQ) for production scale
- [ ] Implement retry with exponential backoff on TinyFish failures
- [ ] Add structured logging + Sentry error tracking
- [ ] Rate limiting on API endpoints (10 req/min per IP)

### Supplier Coverage

- [ ] Test and certify 10 supplier sites for the top 3 SMB procurement categories
- [ ] Industrial: IndiaMART, TradeIndia, ExportersIndia, Alibaba, McMaster-Carr
- [ ] Office: Amazon Business, Staples, Office Depot, Costco Business
- [ ] Tech: Mouser, DigiKey, Arrow Electronics

### Demo Polish

- [ ] Add user authentication (NextAuth or Clerk)
- [ ] Email notification when quote job completes
- [ ] Mobile-responsive results page improvements

---

## Month 1–2: Paid MVP

### Billing

- [ ] Stripe integration
- [ ] Free tier: 5 quote hunts/month
- [ ] Pro: $49/month, unlimited hunts
- [ ] Team: $99/month, 3 seats, shared supplier library

### Acquisition

- [ ] ProductHunt launch
- [ ] Cold email to 50 SMB procurement managers in target verticals
- [ ] LinkedIn content: "We automated our procurement research" case study
- [ ] Goal: 10 paying customers at $49/month

---

## Month 3–4: Authenticated Enrichment

### Feature: Connected Supplier Accounts

- [ ] Allow users to connect their own IndiaMART/Amazon Business login
- [ ] Agent uses their session cookies for authenticated pricing (account-specific rates)
- [ ] Unlocks: member pricing, saved addresses, GST-inclusive quotes

### Feature: Workflow Triggers

- [ ] Zapier integration: trigger quote hunt from new Airtable/Notion row
- [ ] Webhook: POST to user URL when job completes
- [ ] Slack bot: `/quote 500 M8 hex bolts` triggers hunt, posts results to channel

---

## Month 5–6: ERP Integration

### Feature: PO Auto-Creation

- [ ] Connect to Zoho Books, QuickBooks, TallyPrime
- [ ] One-click: approve winning quote → create draft Purchase Order in ERP
- [ ] Auto-fill vendor details from quote result + supplier library

### Feature: Approval Workflow

- [ ] Share report link with manager (read-only quote view)
- [ ] Manager clicks "Approve" → triggers PO creation
- [ ] Email trail for compliance

---

## Year 1: Vertical Editions

### ProcureIQ for Construction

- Suppliers: BuildersMART, JK Lakshmi, UltraTech dealer portals
- Custom fields: grade certifications, load ratings
- Integration: project-level BOM tracking

### ProcureIQ for Pharma

- Suppliers: chemical raw material vendors, excipient suppliers
- Custom fields: CoA requirements, GMP certification status
- Compliance: pharmacopeia grade tracking

### ProcureIQ for F&B

- Suppliers: agricultural commodity markets, FMCG distributors
- Custom fields: seasonal pricing, perishability windows
- Integration: inventory management systems

---

## Year 2: Marketplace Model

### Supplier-Side Network

- Verified suppliers can "claim their profile"
- Suppliers offer ProcureIQ-exclusive pricing tiers
- Buyers see a "ProcureIQ Verified Supplier" badge
- Transforms from tool → marketplace

### Data Product

- Aggregate anonymized pricing data (with consent)
- Sell market intelligence reports: "Average M8 bolt pricing Q3 2026"
- Subscription API for price benchmarking

### Enterprise

- On-premise deployment (Docker) for data-sensitive customers
- SOC 2 Type II certification
- Dedicated agent pools (guaranteed SLA)
- Custom extraction schema builder (no-code)

---

## Defensible Moat (Long-term)

1. **Supplier compatibility data**: Which sites work best for which categories
2. **Agent success rate by supplier**: Hidden reliability scores
3. **Price accuracy benchmarks**: "Our extraction is 94% accurate vs manual check"
4. **Network effects**: More users → more supplier relationships → better pricing
5. **Switching cost**: ERP integrations + approval workflows → high stickiness

---

## Revenue Projections

| Phase | Timeline | MRR | Customers |

|-------|----------|-----|-----------|
| Hackathon | Day 0 | $0 | Waitlist: 11 |
| Paid MVP | Month 2 | $490 | 10 @ $49 |
| Growth | Month 6 | $4,900 | 100 @ $49 |
| Scale | Month 12 | $24,500 | 300 Pro + 50 Team |
| Enterprise | Year 2 | $100k+ | Mix of SMB + enterprise |

**Unit economics at scale:**

- COGS: ~$0.001/quote (LLM) + TinyFish API cost
- Gross margin: 85%+ at Pro tier
- CAC: $50-100 (content + cold email)
- LTV: $588 (avg 12 months at $49)
- LTV/CAC: 6-12x
