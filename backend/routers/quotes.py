import json
import asyncio
from datetime import datetime
import pandas as pd
import io

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db, AsyncSessionLocal
from core.config import get_settings
from models.quote_job import QuoteJob
from models.quote_result import QuoteResult
from models.rfq_draft import RFQDraft
from schemas.quote import QuoteJobCreate, QuoteJobResponse, QuoteJobSummary, QuoteStatusResponse
from schemas.rfq import RFQRequest, RFQResponse
from services.agent_orchestrator import orchestrate_quote_job, get_step_logs
from services.extraction_service import parse_product_query
from services.rfq_generator import generate_rfq_email

router = APIRouter(prefix="/api/quotes", tags=["quotes"])
settings = get_settings()


@router.post("", response_model=dict)
async def create_quote_job(
    payload: QuoteJobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Create a new quote job and fire off agent tasks in the background."""
    # Parse the product query for smart reformulation display
    parsed = await parse_product_query(payload.product_description)

    job = QuoteJob(
        product_description=payload.product_description,
        supplier_urls=json.dumps(payload.supplier_urls),
        status="PENDING",
        total_suppliers=len(payload.supplier_urls),
        completed_suppliers=0,
        failed_suppliers=0,
        parsed_product=parsed.get("product"),
        parsed_grade=parsed.get("grade"),
        parsed_quantity=parsed.get("quantity"),
        parsed_material=parsed.get("material"),
        parsed_search_string=parsed.get("search_string"),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Fire background task
    background_tasks.add_task(orchestrate_quote_job, job.id, AsyncSessionLocal)

    return {
        "job_id": job.id,
        "status": "PENDING",
        "parsed_query": parsed,
        "created_at": job.created_at.isoformat(),
    }


@router.get("", response_model=list[dict])
async def list_quote_jobs(db: AsyncSession = Depends(get_db)):
    """List recent quote jobs for dashboard."""
    result = await db.execute(
        select(QuoteJob).order_by(QuoteJob.created_at.desc()).limit(20)
    )
    jobs = result.scalars().all()

    out = []
    for job in jobs:
        # Find best price result
        res_q = await db.execute(
            select(QuoteResult)
            .where(QuoteResult.job_id == job.id, QuoteResult.is_recommended == True)
            .limit(1)
        )
        best = res_q.scalar_one_or_none()
        out.append({
            "id": job.id,
            "product_description": job.product_description,
            "status": job.status,
            "total_suppliers": job.total_suppliers,
            "completed_suppliers": job.completed_suppliers,
            "best_price": best.unit_price if best else None,
            "best_price_currency": best.currency if best else None,
            "best_supplier_name": best.supplier_name if best else None,
            "human_minutes_saved": job.human_minutes_saved,
            "duration_seconds": job.duration_seconds,
            "created_at": job.created_at.isoformat(),
        })
    return out


@router.get("/{job_id}", response_model=dict)
async def get_quote_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Get full job with all results — used by results page polling."""
    job = await db.get(QuoteJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Quote job not found")

    results_q = await db.execute(
        select(QuoteResult).where(QuoteResult.job_id == job_id)
    )
    results = results_q.scalars().all()

    return {
        "id": job.id,
        "product_description": job.product_description,
        "supplier_urls": json.loads(job.supplier_urls),
        "status": job.status,
        "total_suppliers": job.total_suppliers,
        "completed_suppliers": job.completed_suppliers,
        "failed_suppliers": job.failed_suppliers,
        "human_minutes_saved": job.human_minutes_saved,
        "winner_explanation": json.loads(job.winner_explanation) if job.winner_explanation else None,
        "parsed_query": {
            "product": job.parsed_product,
            "grade": job.parsed_grade,
            "quantity": job.parsed_quantity,
            "material": job.parsed_material,
            "search_string": job.parsed_search_string,
        },
        "duration_seconds": job.duration_seconds,
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "results": [_format_result(r) for r in results],
        "live_steps": get_step_logs(job_id),
    }


@router.get("/{job_id}/status")
async def get_quote_status(job_id: str, db: AsyncSession = Depends(get_db)):
    """Lightweight status endpoint for polling."""
    job = await db.get(QuoteJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Quote job not found")

    results_q = await db.execute(
        select(QuoteResult).where(QuoteResult.job_id == job_id)
    )
    results = results_q.scalars().all()

    return {
        "job_id": job.id,
        "overall_status": job.status,
        "completed": job.completed_suppliers,
        "failed": job.failed_suppliers,
        "total": job.total_suppliers,
        "live_steps": get_step_logs(job_id)[-5:],  # last 5 steps only
        "results": [
            {
                "id": r.id,
                "supplier_url": r.supplier_url,
                "supplier_name": r.supplier_name,
                "status": r.status,
                "unit_price": r.unit_price,
                "currency": r.currency,
            }
            for r in results
        ],
    }


@router.post("/{job_id}/rfq-email", response_model=dict)
async def create_rfq_email(
    job_id: str,
    payload: RFQRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate a formal RFQ email for the selected supplier result."""
    job = await db.get(QuoteJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    result = await db.get(QuoteResult, payload.selected_result_id)
    if not result or result.job_id != job_id:
        raise HTTPException(status_code=404, detail="Result not found")

    rfq_data = await generate_rfq_email(
        product_description=job.product_description,
        supplier_name=result.supplier_name or result.supplier_url,
        unit_price=result.unit_price,
        currency=result.currency,
        moq=result.moq,
        availability=result.availability,
        shipping_days_min=result.shipping_days_min,
        shipping_days_max=result.shipping_days_max,
    )

    draft = RFQDraft(
        job_id=job_id,
        result_id=result.id,
        subject=rfq_data["subject"],
        body=rfq_data["body"],
        recipient_hint=rfq_data.get("recipient_hint"),
    )
    db.add(draft)
    await db.commit()
    await db.refresh(draft)

    return {
        "id": draft.id,
        "subject": draft.subject,
        "body": draft.body,
        "recipient_hint": draft.recipient_hint,
    }


@router.get("/{job_id}/export")
async def export_quotes_csv(job_id: str, db: AsyncSession = Depends(get_db)):
    """Export all quote results as a CRM-ready CSV."""
    job = await db.get(QuoteJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    results_q = await db.execute(
        select(QuoteResult).where(QuoteResult.job_id == job_id)
    )
    results = results_q.scalars().all()

    rows = []
    for r in results:
        rows.append({
            "Product Description": job.product_description,
            "Supplier Name": r.supplier_name or r.supplier_url,
            "Supplier URL": r.supplier_url,
            "Unit Price": r.unit_price,
            "Currency": r.currency,
            "MOQ": r.moq,
            "Shipping Cost": r.shipping_cost,
            "Lead Time (days)": f"{r.shipping_days_min or '?'}-{r.shipping_days_max or '?'}",
            "Availability": r.availability,
            "Confidence": r.confidence,
            "Best Value": "Yes" if r.is_best_value else "No",
            "Fastest": "Yes" if r.is_fastest else "No",
            "Recommended": "Yes" if r.is_recommended else "No",
            "Composite Score": round(r.composite_score, 4) if r.composite_score else None,
            "Status": r.status,
            "Product URL": r.product_url,
            "Quote Date": job.created_at.strftime("%Y-%m-%d %H:%M"),
            "Time Saved (minutes)": job.human_minutes_saved,
        })

    df = pd.DataFrame(rows)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)

    filename = f"procureiq_quotes_{job_id[:8]}.csv"
    return StreamingResponse(
        io.BytesIO(buf.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _format_result(r: QuoteResult) -> dict:
    steps = []
    if r.agent_steps_log:
        try:
            steps = json.loads(r.agent_steps_log)
        except Exception:
            steps = []
    return {
        "id": r.id,
        "supplier_url": r.supplier_url,
        "supplier_name": r.supplier_name,
        "unit_price": r.unit_price,
        "currency": r.currency,
        "price_per_unit_label": r.price_per_unit_label,
        "moq": r.moq,
        "shipping_cost": r.shipping_cost,
        "shipping_days_min": r.shipping_days_min,
        "shipping_days_max": r.shipping_days_max,
        "availability": r.availability,
        "product_url": r.product_url,
        "product_name": r.product_name,
        "confidence": r.confidence,
        "confidence_reason": r.confidence_reason,
        "composite_score": r.composite_score,
        "is_best_value": r.is_best_value,
        "is_fastest": r.is_fastest,
        "is_recommended": r.is_recommended,
        "agent_steps": steps,
        "status": r.status,
        "error_message": r.error_message,
        "completed_at": r.completed_at.isoformat() if r.completed_at else None,
    }