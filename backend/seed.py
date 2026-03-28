"""
Seed script — run once on startup (safe to re-run, checks for existing data).
Populates default suppliers and optional demo quote history.
"""
import asyncio
import json
from datetime import datetime, timedelta
import random

from core.database import AsyncSessionLocal, init_db
from models.supplier import Supplier
from models.quote_job import QuoteJob
from models.quote_result import QuoteResult
from sqlalchemy import select


DEFAULT_SUPPLIERS = [
    {
        "name": "IndiaMART",
        "url": "https://www.indiamart.com",
        "logo_url": "https://4.imimg.com/data4/KK/NR/MY-1740821/indiamart-logo.png",
        "category": "Industrial & B2B",
        "is_verified": True,
        "trust_score": 94,
        "seller_count": "12,000+",
        "avg_response_time": "4 hrs",
    },
    {
        "name": "Amazon Business",
        "url": "https://www.amazon.in",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
        "category": "General Procurement",
        "is_verified": True,
        "trust_score": 98,
        "seller_count": "2M+",
        "avg_response_time": "Instant",
    },
    {
        "name": "Alibaba",
        "url": "https://www.alibaba.com",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Alibaba_Group_logo.svg",
        "category": "Global Manufacturing",
        "is_verified": True,
        "trust_score": 87,
        "seller_count": "200,000+",
        "avg_response_time": "24 hrs",
    },
    {
        "name": "TradeIndia",
        "url": "https://www.tradeindia.com",
        "logo_url": None,
        "category": "Industrial & B2B",
        "is_verified": True,
        "trust_score": 82,
        "seller_count": "5,000+",
        "avg_response_time": "6 hrs",
    },
    {
        "name": "ExportersIndia",
        "url": "https://www.exportersindia.com",
        "logo_url": None,
        "category": "Export & Manufacturing",
        "is_verified": False,
        "trust_score": 76,
        "seller_count": "2,000+",
        "avg_response_time": "12 hrs",
    },
]

DEMO_JOBS = [
    {
        "product_description": "500 units M8 zinc-plated hex bolts grade 8.8",
        "results": [
            {"supplier_name": "IndiaMART Vendor", "unit_price": 2.45, "currency": "INR", "moq": 100, "shipping_days_min": 3, "shipping_days_max": 5, "availability": "In Stock", "confidence": "HIGH", "is_recommended": True, "is_best_value": False, "is_fastest": False},
            {"supplier_name": "Amazon Business", "unit_price": 2.98, "currency": "INR", "moq": 50, "shipping_days_min": 1, "shipping_days_max": 2, "availability": "In Stock", "confidence": "HIGH", "is_recommended": False, "is_best_value": False, "is_fastest": True},
            {"supplier_name": "Alibaba Supplier", "unit_price": 1.89, "currency": "USD", "moq": 1000, "shipping_days_min": 10, "shipping_days_max": 15, "availability": "Ships in 12 days", "confidence": "MEDIUM", "is_recommended": False, "is_best_value": True, "is_fastest": False},
        ],
    },
    {
        "product_description": "A4 copy paper 500 sheets 80gsm - 10 reams",
        "results": [
            {"supplier_name": "Amazon Business", "unit_price": 4.20, "currency": "USD", "moq": 5, "shipping_days_min": 1, "shipping_days_max": 2, "availability": "In Stock", "confidence": "HIGH", "is_recommended": True, "is_best_value": False, "is_fastest": True},
            {"supplier_name": "IndiaMART Vendor", "unit_price": 3.85, "currency": "USD", "moq": 50, "shipping_days_min": 4, "shipping_days_max": 6, "availability": "In Stock", "confidence": "HIGH", "is_recommended": False, "is_best_value": True, "is_fastest": False},
            {"supplier_name": "TradeIndia Seller", "unit_price": 4.50, "currency": "USD", "moq": 10, "shipping_days_min": 3, "shipping_days_max": 4, "availability": "Limited Stock", "confidence": "MEDIUM", "is_recommended": False, "is_best_value": False, "is_fastest": False},
        ],
    },
    {
        "product_description": "USB-C to USB-A cable 1m braided - 20 units",
        "results": [
            {"supplier_name": "Amazon Business", "unit_price": 3.99, "currency": "USD", "moq": 10, "shipping_days_min": 1, "shipping_days_max": 1, "availability": "In Stock — Same Day", "confidence": "HIGH", "is_recommended": True, "is_best_value": False, "is_fastest": True},
            {"supplier_name": "Alibaba OEM", "unit_price": 1.20, "currency": "USD", "moq": 500, "shipping_days_min": 14, "shipping_days_max": 21, "availability": "Made to Order", "confidence": "MEDIUM", "is_recommended": False, "is_best_value": True, "is_fastest": False},
            {"supplier_name": "IndiaMART", "unit_price": 2.80, "currency": "USD", "moq": 25, "shipping_days_min": 3, "shipping_days_max": 5, "availability": "In Stock", "confidence": "HIGH", "is_recommended": False, "is_best_value": False, "is_fastest": False},
        ],
    },
]


async def seed_suppliers():
    """Seed default suppliers if not already present."""
    async with AsyncSessionLocal() as db:
        existing = (await db.execute(select(Supplier).limit(1))).scalar_one_or_none()
        if existing:
            return  # Already seeded

        for s in DEFAULT_SUPPLIERS:
            supplier = Supplier(**s)
            db.add(supplier)
        await db.commit()
        print(f"Seeded {len(DEFAULT_SUPPLIERS)} default suppliers")


async def seed_demo_jobs():
    """Seed demo quote history so dashboard looks populated on first run."""
    async with AsyncSessionLocal() as db:
        existing = (await db.execute(select(QuoteJob).limit(1))).scalar_one_or_none()
        if existing:
            return

        suppliers = (await db.execute(select(Supplier))).scalars().all()
        supplier_urls = [s.url for s in suppliers[:3]]

        for i, demo in enumerate(DEMO_JOBS):
            created = datetime.utcnow() - timedelta(days=random.randint(1, 7), hours=random.randint(0, 12))
            completed = created + timedelta(seconds=random.randint(75, 120))

            job = QuoteJob(
                product_description=demo["product_description"],
                supplier_urls=json.dumps(supplier_urls),
                status="COMPLETE",
                total_suppliers=3,
                completed_suppliers=3,
                failed_suppliers=0,
                human_minutes_saved=150,
                created_at=created,
                completed_at=completed,
            )
            db.add(job)
            await db.flush()

            for r_data in demo["results"]:
                result = QuoteResult(
                    job_id=job.id,
                    supplier_url=supplier_urls[demo["results"].index(r_data) % len(supplier_urls)],
                    status="COMPLETE",
                    shipping_cost=round(random.uniform(0, 50), 2),
                    composite_score=round(random.uniform(0.6, 0.95), 4),
                    agent_steps_log=json.dumps([
                        "Navigated to supplier homepage",
                        "Submitted product search",
                        "Identified best matching product",
                        "Extracted pricing table",
                        "Confirmed availability",
                    ]),
                    created_at=created,
                    completed_at=completed,
                    **r_data,
                )
                db.add(result)

            # Set recommended result id
            rec_result = next((r for r in demo["results"] if r["is_recommended"]), None)
            if rec_result:
                job.winner_explanation = json.dumps([
                    f"• Best overall score considering price, speed, and availability",
                    f"• Ships in {rec_result.get('shipping_days_min', 3)}-{rec_result.get('shipping_days_max', 5)} days — faster than 2 of 3 vendors",
                    f"• Confirmed in stock for requested quantity with HIGH confidence",
                ])

        await db.commit()
        print(f"Seeded {len(DEMO_JOBS)} demo quote jobs")


async def main():
    await init_db()
    await seed_suppliers()
    await seed_demo_jobs()
    print("Database seeded successfully")


if __name__ == "__main__":
    asyncio.run(main())
