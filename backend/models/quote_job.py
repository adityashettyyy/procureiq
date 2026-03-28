import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base


class QuoteJob(Base):
    __tablename__ = "quote_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_description: Mapped[str] = mapped_column(String, nullable=False)
    # JSON array stored as string: '["url1","url2","url3"]'
    supplier_urls: Mapped[str] = mapped_column(String, nullable=False)
    # PENDING | RUNNING | PARTIAL | COMPLETE | FAILED
    status: Mapped[str] = mapped_column(String, default="PENDING")
    total_suppliers: Mapped[int] = mapped_column(Integer, default=0)
    completed_suppliers: Mapped[int] = mapped_column(Integer, default=0)
    failed_suppliers: Mapped[int] = mapped_column(Integer, default=0)
    recommended_result_id: Mapped[str | None] = mapped_column(String, nullable=True)
    human_minutes_saved: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Parsed query fields (from smart query reformulation)
    parsed_product: Mapped[str | None] = mapped_column(String, nullable=True)
    parsed_grade: Mapped[str | None] = mapped_column(String, nullable=True)
    parsed_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parsed_material: Mapped[str | None] = mapped_column(String, nullable=True)
    parsed_search_string: Mapped[str | None] = mapped_column(String, nullable=True)
    # Winner recommendation explanation bullets (JSON)
    winner_explanation: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    @property
    def duration_seconds(self) -> float | None:
        if self.completed_at and self.created_at:
            return (self.completed_at - self.created_at).total_seconds()
        return None
