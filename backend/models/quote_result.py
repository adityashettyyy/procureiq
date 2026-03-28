import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base


class QuoteResult(Base):
    __tablename__ = "quote_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    supplier_url: Mapped[str] = mapped_column(String, nullable=False)
    supplier_name: Mapped[str | None] = mapped_column(String, nullable=True)
    # Pricing
    unit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String, default="USD")
    price_per_unit_label: Mapped[str | None] = mapped_column(String, nullable=True)
    moq: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shipping_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    shipping_days_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shipping_days_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    availability: Mapped[str | None] = mapped_column(String, nullable=True)
    product_url: Mapped[str | None] = mapped_column(String, nullable=True)
    product_name: Mapped[str | None] = mapped_column(String, nullable=True)
    # Quality signals
    confidence: Mapped[str] = mapped_column(String, default="LOW")  # HIGH|MEDIUM|LOW
    confidence_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    composite_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Verification
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    trust_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Winner tags
    is_best_value: Mapped[bool] = mapped_column(Boolean, default=False)
    is_fastest: Mapped[bool] = mapped_column(Boolean, default=False)
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    # Agent metadata
    agent_steps_log: Mapped[str | None] = mapped_column(String, nullable=True)  # JSON
    tinyfish_task_id: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_html_snippet: Mapped[str | None] = mapped_column(String, nullable=True)
    # Status
    status: Mapped[str] = mapped_column(String, default="RUNNING")  # RUNNING|COMPLETE|FAILED|TIMEOUT|BLOCKED
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
