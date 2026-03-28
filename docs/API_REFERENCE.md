# ProcureIQ — API Reference

Base URL: `http://localhost:8000` (local) or `https://your-app.railway.app` (prod)

All endpoints return JSON unless noted. All timestamps are UTC ISO 8601.

---

## Health

### GET /health

```json
{ "status": "ok", "version": "1.0.0", "db": "connected" }
```

---

## Quotes

### POST /api/quotes

Create a new quote job and start agent tasks.

**Request**

```json
{
  "product_description": "500 units M8 zinc-plated hex bolts grade 8.8",
  "supplier_urls": [
    "https://www.indiamart.com",
    "https://www.amazon.in",
    "https://www.alibaba.com"
  ]
}
```

**Response** `201`

```json
{
  "job_id": "uuid",
  "status": "PENDING",
  "parsed_query": {
    "product": "Hex Bolt M8",
    "grade": "8.8",
    "quantity": 500,
    "material": "Zinc-plated",
    "search_string": "M8 hex bolt zinc plated grade 8.8 bulk"
  },
  "created_at": "2025-10-01T12:00:00Z"
}
```

---

### GET /api/quotes

List recent quote jobs (last 20).

**Response** `200` — Array of job summaries

```json
[
  {
    "id": "uuid",
    "product_description": "...",
    "status": "COMPLETE",
    "total_suppliers": 3,
    "completed_suppliers": 3,
    "best_price": 2.45,
    "best_price_currency": "USD",
    "best_supplier_name": "IndiaMART Vendor",
    "human_minutes_saved": 150,
    "duration_seconds": 91.4,
    "created_at": "..."
  }
]
```

---

### GET /api/quotes/{job_id}

Full job with all results and live steps.

**Response** `200`

```json
{
  "id": "uuid",
  "product_description": "...",
  "supplier_urls": ["url1", "url2", "url3"],
  "status": "COMPLETE",
  "total_suppliers": 3,
  "completed_suppliers": 3,
  "failed_suppliers": 0,
  "human_minutes_saved": 150,
  "winner_explanation": ["• 23% cheaper...", "• Ships in 3-5 days...", "• Confirmed in stock..."],
  "parsed_query": { ... },
  "duration_seconds": 91.4,
  "live_steps": ["[indiamart.com] Navigating...", "..."],
  "results": [ /* see QuoteResult schema below */ ],
  "created_at": "...",
  "completed_at": "..."
}
```

---

### GET /api/quotes/{job_id}/status

Lightweight polling endpoint. Use this instead of full job for polling.

**Response** `200`

```json
{
  "job_id": "uuid",
  "overall_status": "RUNNING",
  "completed": 1,
  "failed": 0,
  "total": 3,
  "live_steps": ["last 5 steps..."],
  "results": [
    { "id": "...", "supplier_url": "...", "supplier_name": "...", "status": "COMPLETE", "unit_price": 2.45, "currency": "USD" }
  ]
}
```

---

### POST /api/quotes/{job_id}/rfq-email

Generate a formal RFQ email for the selected supplier.

**Request**

```json
{ "selected_result_id": "quote_result_uuid" }
```

**Response** `200`

```json
{
  "id": "rfq_draft_uuid",
  "subject": "Request for Quotation — M8 Hex Bolts (500 units)",
  "body": "Dear IndiaMART Vendor Team,\n\nWe are writing to formally...",
  "recipient_hint": "Contact via IndiaMART messaging or their listed email"
}
```

---

### GET /api/quotes/{job_id}/export

Download all results as CSV.

**Response** `200` — `text/csv` file download

Columns: `Product Description, Supplier Name, Supplier URL, Unit Price, Currency, MOQ, Shipping Cost, Lead Time (days), Availability, Confidence, Best Value, Fastest, Recommended, Status, Product URL, Quote Date`

---

## Suppliers

### GET /api/suppliers

```json
[
  {
    "id": "uuid",
    "name": "IndiaMART",
    "url": "https://www.indiamart.com",
    "logo_url": null,
    "category": "Industrial & B2B",
    "is_active": true,
    "is_verified": true,
    "trust_score": 94,
    "seller_count": "12,000+",
    "avg_response_time": "4 hrs",
    "created_at": "..."
  }
]
```

### POST /api/suppliers

```json
// Request
{ "name": "TradeIndia", "url": "https://www.tradeindia.com", "category": "B2B" }

// Response — full Supplier object
```

### PUT /api/suppliers/{id}

Partial update. All fields optional.

### DELETE /api/suppliers/{id}

Soft delete (sets `is_active=false`).

```json
{ "deleted": true }
```

---

## Metrics

### GET /api/metrics/summary

```json
{
  "total_jobs": 47,
  "successful_jobs": 44,
  "total_quotes_collected": 129,
  "total_hours_saved": 117.5,
  "total_minutes_saved": 7050
}
```

### GET /api/metrics/active-agents

```json
{ "active_agents": 3 }
```

---

## QuoteResult Schema (full)

```json
{
  "id": "uuid",
  "supplier_url": "https://www.indiamart.com",
  "supplier_name": "IndiaMART Vendor",
  "unit_price": 2.45,
  "currency": "USD",
  "price_per_unit_label": "per piece",
  "moq": 100,
  "shipping_cost": 8.50,
  "shipping_days_min": 3,
  "shipping_days_max": 5,
  "availability": "In Stock",
  "product_url": "https://www.indiamart.com/proddetail/...",
  "product_name": "M8 x 25mm Hex Bolt Zinc Plated Grade 8.8",
  "confidence": "HIGH",
  "confidence_reason": "Price confirmed in bulk pricing table at 500-unit tier",
  "composite_score": 0.8734,
  "is_best_value": false,
  "is_fastest": false,
  "is_recommended": true,
  "agent_steps": ["Navigated to homepage", "Searched...", "Extracted pricing"],
  "status": "COMPLETE",
  "error_message": null,
  "completed_at": "..."
}
```

**Status values:** `RUNNING | COMPLETE | FAILED | TIMEOUT | BLOCKED | NOT_FOUND`

**Confidence values:** `HIGH | MEDIUM | LOW`
