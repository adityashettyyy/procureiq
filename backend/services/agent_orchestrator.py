"""
Agent Orchestrator: coordinates parallel TinyFish agent tasks,
stores results, triggers comparison engine.

This is the most critical service — treat it carefully.
"""
import asyncio
import json
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.quote_job import QuoteJob
from models.quote_result import QuoteResult
from services.tinyfish_client import get_tinyfish_client
from services.extraction_service import extract_quote_from_html, generate_winner_explanation
from services.comparison_engine import compute_scores, estimate_minutes_saved
from core.config import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

# In-memory step logs per job_id (for live feed)
_step_logs: dict[str, list[str]] = {}

# DB write lock (prevents SQLite race conditions)
_db_write_lock = asyncio.Lock()


async def orchestrate_quote_job(job_id: str, db_factory) -> None:
    """
    Main orchestration function. Called as a background task.
    Spawns parallel agent tasks, collects results, triggers comparison.

    CRITICAL FIX: Capture all job field values as plain Python strings
    INSIDE the session before it closes. SQLAlchemy ORM objects become
    detached after 'async with db_factory()' exits — accessing attributes
    on a detached object raises an error that silently kills the background
    task, leaving the job stuck in RUNNING status forever.
    """
    # ── Capture plain values inside session ─────────────────
    supplier_urls: list[str] = []
    product_description: str = ""
    search_string: str = ""

    try:
        async with db_factory() as db:
            job = await _get_job(db, job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return

            # ✅ Extract to plain Python strings before session closes
            supplier_urls     = json.loads(job.supplier_urls)
            product_description = str(job.product_description)
            search_string     = str(job.parsed_search_string or job.product_description)

            _step_logs[job_id] = []
            logger.info(f"Starting orchestration for job {job_id}: {len(supplier_urls)} suppliers")

            job.status = "RUNNING"
            await db.commit()
            # Session closes here — job object is now detached, never use it again

    except Exception as e:
        logger.error(f"Orchestrator setup failed for {job_id}: {e}")
        return

    # ── DEMO MODE ────────────────────────────────────────────
    if settings.demo_mode:
        await _run_demo_mode(job_id, supplier_urls, db_factory)
        return

    # ── LIVE MODE: parallel agents ───────────────────────────
    try:
        tasks = [
            _run_single_agent(
                job_id,
                url,
                product_description,    # ✅ plain string — safe outside session
                search_string,          # ✅ plain string — safe outside session
                db_factory,
            )
            for url in supplier_urls
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    except Exception as e:
        logger.error(f"Orchestrator agents failed for {job_id}: {e}")

    finally:
        # ✅ ALWAYS runs — job status never stays RUNNING permanently
        await _finalise_job(job_id, db_factory)


async def _run_single_agent(
    job_id: str,
    supplier_url: str,
    product_description: str,
    search_string: str,
    db_factory,
) -> None:
    """Run one TinyFish agent task and store the result."""
    client = get_tinyfish_client()

    def log_step(step: str):
        if job_id in _step_logs:
            domain = supplier_url.split("//")[-1].split("/")[0]
            entry = f"[{domain}] {step}"
            _step_logs[job_id].append(entry)
            logger.info(entry)

    # Create result row as RUNNING
    async with db_factory() as db:
        result = QuoteResult(
            job_id=job_id,
            supplier_url=supplier_url,
            status="RUNNING",
        )
        async with _db_write_lock:
            db.add(result)
            await db.commit()
            await db.refresh(result)
        result_id = result.id

    log_step("Agent starting...")
    log_step(f"Navigating to {supplier_url}...")

    try:
        agent_output = await client.run_task_and_wait(
            supplier_url=supplier_url,
            product_description=product_description,
            search_string=search_string,
            on_step_callback=lambda s: log_step(s),
        )

        agent_status = agent_output.get("status", "FAILED")
        html = agent_output.get("html", "")
        steps = agent_output.get("steps", [])
        task_id = agent_output.get("task_id")

        if agent_status == "COMPLETE":
            log_step("Extracting pricing data...")
            # Use TinyFish structured result directly if available
            # This avoids needing OpenAI and is more accurate
            structured = agent_output.get("structured") or {}
            if structured and structured.get("unit_price"):
                extracted = structured
                log_step(f"Structured extraction complete — confidence: {extracted.get('confidence', 'HIGH')}")
            elif html:
                extracted = await extract_quote_from_html(html, product_description, supplier_url)
                log_step(f"HTML extraction complete — confidence: {extracted.get('confidence', 'LOW')}")
            else:
                from services.extraction_service import _empty_quote
                extracted = _empty_quote(supplier_url, "No data returned from agent")
                log_step("No extractable data returned")

            async with db_factory() as db:
                res = await db.get(QuoteResult, result_id)
                if res:
                    res.supplier_name = extracted.get("supplier_name")
                    res.product_name = extracted.get("product_name")
                    res.product_url = extracted.get("product_url")
                    res.unit_price = extracted.get("unit_price")
                    res.currency = extracted.get("currency") or "USD"
                    res.price_per_unit_label = extracted.get("price_per_unit_label")
                    res.moq = extracted.get("moq")
                    res.shipping_cost = extracted.get("shipping_cost")
                    res.shipping_days_min = extracted.get("shipping_days_min")
                    res.shipping_days_max = extracted.get("shipping_days_max")
                    res.availability = extracted.get("availability")
                    res.confidence = extracted.get("confidence", "LOW")
                    res.confidence_reason = extracted.get("confidence_reason")
                    res.agent_steps_log = json.dumps(steps + _step_logs.get(job_id, []))
                    res.tinyfish_task_id = task_id
                    res.raw_html_snippet = html[:2000]
                    res.status = "COMPLETE"
                    res.completed_at = datetime.utcnow()
                    async with _db_write_lock:
                        await db.commit()

            # Increment job counter
            await _increment_job_counter(job_id, "completed", db_factory)

        else:
            error_msg = agent_output.get("error") or agent_status
            log_step(f"Agent returned: {agent_status}")
            async with db_factory() as db:
                res = await db.get(QuoteResult, result_id)
                if res:
                    res.status = agent_status
                    res.error_message = error_msg
                    res.agent_steps_log = json.dumps(steps)
                    res.completed_at = datetime.utcnow()
                    async with _db_write_lock:
                        await db.commit()
            await _increment_job_counter(job_id, "failed", db_factory)

    except Exception as e:
        logger.error(f"Agent error for {supplier_url}: {e}")
        log_step(f"Error: {str(e)[:80]}")
        async with db_factory() as db:
            res = await db.get(QuoteResult, result_id)
            if res:
                res.status = "FAILED"
                res.error_message = str(e)
                res.completed_at = datetime.utcnow()
                async with _db_write_lock:
                    await db.commit()
        await _increment_job_counter(job_id, "failed", db_factory)


async def _finalise_job(job_id: str, db_factory) -> None:
    """Score results, tag winners, update job status."""
    async with db_factory() as db:
        job = await _get_job(db, job_id)
        if not job:
            return

        results_q = await db.execute(
            select(QuoteResult).where(QuoteResult.job_id == job_id)
        )
        results = list(results_q.scalars().all())

        # Score and tag winners
        scored = compute_scores(results)

        # Get winner for explanation
        winner = next((r for r in scored if r.is_recommended), None)
        if winner:
            job.recommended_result_id = winner.id
            quote_dicts = [
                {
                    "id": r.id,
                    "supplier": r.supplier_name,
                    "price": r.unit_price,
                    "currency": r.currency,
                    "shipping_days": r.shipping_days_max,
                    "availability": r.availability,
                }
                for r in scored
                if r.status == "COMPLETE"
            ]
            explanations = await generate_winner_explanation(quote_dicts, winner.id)
            job.winner_explanation = json.dumps(explanations)

        # Determine final job status
        completed = sum(1 for r in results if r.status == "COMPLETE")
        failed = sum(1 for r in results if r.status in ("FAILED", "TIMEOUT", "BLOCKED", "NOT_FOUND"))

        if completed == 0:
            job.status = "FAILED"
        elif failed > 0:
            job.status = "PARTIAL"
        else:
            job.status = "COMPLETE"

        job.human_minutes_saved = estimate_minutes_saved(settings.human_benchmark_minutes)
        job.completed_at = datetime.utcnow()

        async with _db_write_lock:
            await db.commit()

    logger.info(f"Job {job_id} finalised: {job.status}")


async def _increment_job_counter(job_id: str, counter: str, db_factory) -> None:
    """Safely increment completed or failed counter on job."""
    async with db_factory() as db:
        job = await _get_job(db, job_id)
        if not job:
            return
        if counter == "completed":
            job.completed_suppliers += 1
        elif counter == "failed":
            job.failed_suppliers += 1
        async with _db_write_lock:
            await db.commit()


async def _get_job(db: AsyncSession, job_id: str) -> QuoteJob | None:
    result = await db.execute(select(QuoteJob).where(QuoteJob.id == job_id))
    return result.scalar_one_or_none()


async def _run_demo_mode(job_id: str, supplier_urls: list[str], db_factory) -> None:
    """
    Demo mode: return realistic simulated results based on input URLs.
    Generates varied prices and supplier names derived from URLs.
    Useful when live agents are unreliable during the demo.
    """
    import random

    def generate_demo_result(url: str, product_description: str) -> dict:
        """Generate a realistic demo result based on URL and product."""
        # Extract domain for supplier name
        domain = url.split("//")[-1].split("/")[0].split(".")[-2].title()
        
        # Base prices vary by product type (rough heuristics)
        product_lower = product_description.lower()
        if "bolt" in product_lower or "screw" in product_lower:
            base_price = random.uniform(1.50, 3.50)
        elif "paper" in product_lower:
            base_price = random.uniform(2.00, 5.00)
        elif "cable" in product_lower or "usb" in product_lower:
            base_price = random.uniform(2.00, 6.00)
        else:
            base_price = random.uniform(1.00, 10.00)
        
        # Add some variation
        unit_price = round(base_price * random.uniform(0.8, 1.5), 2)
        
        # MOQ varies
        moq_options = [1, 10, 25, 50, 100, 500, 1000]
        moq = random.choice(moq_options)
        
        # Shipping costs
        shipping_cost = round(random.uniform(0, 50), 2) if random.random() > 0.3 else 0
        
        # Lead times and verification based on supplier
        url_lower = url.lower()
        if "amazon" in url_lower:
            shipping_days_min, shipping_days_max = 1, 2
            availability = "In Stock — Ships Today"
            confidence = "HIGH"
            is_verified = True
            trust_score = random.randint(95, 100)
        elif "alibaba" in url_lower or "china" in url_lower:
            shipping_days_min, shipping_days_max = 10, 21
            availability = "Ships from China — Lead time 14 days"
            confidence = "MEDIUM"
            is_verified = random.random() > 0.3  # 70% verified
            trust_score = random.randint(70, 90)
        elif "mcmaster" in url_lower or "grainger" in url_lower:
            shipping_days_min, shipping_days_max = 2, 5
            availability = "In Stock — Ships within 24h"
            confidence = "HIGH"
            is_verified = True
            trust_score = random.randint(90, 98)
        else:
            shipping_days_min = random.randint(2, 7)
            shipping_days_max = shipping_days_min + random.randint(1, 5)
            availability = random.choice(["In Stock", "Limited Stock", "Made to Order"])
            confidence = random.choice(["HIGH", "MEDIUM"])
            is_verified = random.random() > 0.5  # 50% verified for others
            trust_score = random.randint(60, 95)
        
        return {
            "supplier_name": f"{domain} Supplier",
            "unit_price": unit_price,
            "currency": "USD",
            "moq": moq,
            "shipping_cost": shipping_cost,
            "shipping_days_min": shipping_days_min,
            "shipping_days_max": shipping_days_max,
            "availability": availability,
            "confidence": confidence,
            "confidence_reason": f"Price extracted from {domain} product listing",
            "is_verified": is_verified,
            "trust_score": trust_score,
        }

    demo_steps = [
        "Navigating to supplier homepage...",
        "Located search bar",
        "Submitted product query",
        "Evaluating search results...",
        "Found best matching product",
        "Extracting pricing table...",
        "Confirmed stock availability",
        "Extraction complete ✓",
    ]

    # Get product description for price generation
    async with db_factory() as db:
        job = await _get_job(db, job_id)
        product_description = job.product_description if job else "generic product"

    for i, url in enumerate(supplier_urls):
        await asyncio.sleep(settings.demo_job_delay_seconds + random.uniform(0.5, 2.0))
        demo = generate_demo_result(url, product_description)

        async with db_factory() as db:
            result = QuoteResult(
                job_id=job_id,
                supplier_url=url,
                status="COMPLETE",
                **{k: v for k, v in demo.items()},
                agent_steps_log=json.dumps(demo_steps),
                completed_at=datetime.utcnow(),
            )
            async with _db_write_lock:
                db.add(result)
                await db.commit()

        await _increment_job_counter(job_id, "completed", db_factory)
        if job_id in _step_logs:
            domain = url.split("//")[-1].split("/")[0]
            _step_logs[job_id].extend([f"[{domain}] {s}" for s in demo_steps])
            
    await _finalise_job(job_id, db_factory)        


def get_step_logs(job_id: str) -> list[str]:
    """Return current step log for a job (for live feed)."""
    return _step_logs.get(job_id, [])


def clear_step_logs(job_id: str) -> None:
    _step_logs.pop(job_id, None)