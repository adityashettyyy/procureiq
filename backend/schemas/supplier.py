from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SupplierCreate(BaseModel):
    name: str
    url: str
    logo_url: Optional[str] = None
    category: Optional[str] = None


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    logo_url: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierResponse(BaseModel):
    id: str
    name: str
    url: str
    logo_url: Optional[str] = None
    category: Optional[str] = None
    is_active: bool
    is_verified: bool
    trust_score: Optional[int] = None
    seller_count: Optional[str] = None
    avg_response_time: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
