from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from models.quote_job import QuoteJob
from models.quote_result import QuoteResult

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/summary")
async def get_metrics_summary(db: AsyncSession = Depends(get_db)):
    total_jobs = (await db.execute(select(func.count(QuoteJob.id)))).scalar() or 0
    successful_jobs = (
        await db.execute(
            select(func.count(QuoteJob.id)).where(
                QuoteJob.status.in_(["COMPLETE", "PARTIAL"])
            )
        )
    ).scalar() or 0
    total_quotes = (
        await db.execute(
            select(func.count(QuoteResult.id)).where(QuoteResult.status == "COMPLETE")
        )
    ).scalar() or 0
    total_minutes_saved = (
        await db.execute(
            select(func.sum(QuoteJob.human_minutes_saved)).where(
                QuoteJob.human_minutes_saved.isnot(None)
            )
        )
    ).scalar() or 0

    return {
        "total_jobs": total_jobs,
        "successful_jobs": successful_jobs,
        "total_quotes_collected": total_quotes,
        "total_hours_saved": round(total_minutes_saved / 60, 1),
        "total_minutes_saved": total_minutes_saved,
    }


@router.get("/active-agents")
async def get_active_agents(db: AsyncSession = Depends(get_db)):
    count = (
        await db.execute(
            select(func.count(QuoteJob.id)).where(QuoteJob.status == "RUNNING")
        )
    ).scalar() or 0
    return {"active_agents": count}
