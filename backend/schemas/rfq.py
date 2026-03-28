from pydantic import BaseModel
from typing import Optional


class RFQRequest(BaseModel):
    selected_result_id: str


class RFQResponse(BaseModel):
    id: str
    subject: str
    body: str
    recipient_hint: Optional[str] = None
