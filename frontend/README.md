# ProcureIQ — Frontend

Next.js 14 + Tailwind CSS + TypeScript

## Setup

```bash
npm install
cp ../.env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
# → http://localhost:3000
```

## Pages

| Route | Page | Purpose |
|---|---|---|
| `/` | Landing | Hero, how it works, live metrics |
| `/dashboard` | Dashboard | Quote history, stats, quick actions |
| `/quotes/new` | New Quote | Product input + supplier selector |
| `/quotes/[id]` | Results | Live agent feed, quote cards, RFQ |
| `/suppliers` | Suppliers | Manage supplier library |

## Key Components

| Component | Purpose |
|---|---|
| `AppShell` | Nav bar + layout wrapper |
| `TimeSavedCounter` | Animated benchmark counter |
| `ParsedQueryBanner` | Smart query reformulation display |
| `RFQModal` | RFQ email generation modal |

## Demo Tips

- The results page polls `/api/quotes/{id}/status` every 2.5 seconds
- Cards reveal with a staggered 2.5s delay for visual impact
- Agent monologue typewriter effect shows even before live steps arrive
- `DEMO_MODE=true` on backend returns instant pre-baked results

## Environment Variables

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000   # Backend URL
NEXT_PUBLIC_APP_NAME=ProcureIQ
```
