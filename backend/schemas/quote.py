from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime
from typing import Optional


# ── Requests ────────────────────────────────────────────────

class QuoteJobCreate(BaseModel):
    product_description: str
    supplier_urls: list[str]

    @field_validator("supplier_urls")
    @classmethod
    def validate_urls(cls, v):
        if not v:
            raise ValueError("At least one supplier URL is required")
        if len(v) > 3:
            raise ValueError("Maximum 3 supplier URLs allowed")
        return v

    @field_validator("product_description")
    @classmethod
    def validate_description(cls, v):
        if len(v.strip()) < 5:
            raise ValueError("Product description too short")
        return v.strip()


# ── Responses ───────────────────────────────────────────────

class ParsedQuery(BaseModel):
    product: Optional[str] = None
    grade: Optional[str] = None
    quantity: Optional[int] = None
    material: Optional[str] = None
    search_string: Optional[str] = None


class QuoteResultResponse(BaseModel):
    id: str
    supplier_url: str
    supplier_name: Optional[str] = None
    unit_price: Optional[float] = None
    currency: str = "USD"
    price_per_unit_label: Optional[str] = None
    moq: Optional[int] = None
    shipping_cost: Optional[float] = None
    shipping_days_min: Optional[int] = None
    shipping_days_max: Optional[int] = None
    availability: Optional[str] = None
    product_url: Optional[str] = None
    product_name: Optional[str] = None
    confidence: str = "LOW"
    confidence_reason: Optional[str] = None
    composite_score: Optional[float] = None
    is_best_value: bool = False
    is_fastest: bool = False
    is_recommended: bool = False
    agent_steps_log: Optional[list[str]] = None
    status: str
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuoteJobResponse(BaseModel):
    id: str
    product_description: str
    supplier_urls: list[str]
    status: str
    total_suppliers: int
    completed_suppliers: int
    failed_suppliers: int
    human_minutes_saved: Optional[int] = None
    winner_explanation: Optional[list[str]] = None
    parsed_query: Optional[ParsedQuery] = None
    results: list[QuoteResultResponse] = []
    duration_seconds: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuoteJobSummary(BaseModel):
    id: str
    product_description: str
    status: str
    total_suppliers: int
    completed_suppliers: int
    best_price: Optional[float] = None
    best_price_currency: Optional[str] = None
    best_supplier_name: Optional[str] = None
    human_minutes_saved: Optional[int] = None
    duration_seconds: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class QuoteStatusResponse(BaseModel):
    job_id: str
    overall_status: str
    completed: int
    total: int
    results: list[dict]
