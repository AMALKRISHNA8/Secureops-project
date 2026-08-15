"""
Pydantic schemas for alert endpoints.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class AlertUpdate(BaseModel):
    """Schema for updating an alert's status."""
    status: str = Field(..., pattern=r"^(open|investigating|resolved)$")


class AlertEventInfo(BaseModel):
    """Nested event summary within an alert."""
    id: str
    source: str
    source_ip: Optional[str] = None
    event_type: str
    severity: str
    timestamp: datetime

    model_config = {"from_attributes": True}


class AlertResponse(BaseModel):
    """Schema for a single alert response."""
    id: str
    event_id: str
    rule_name: str
    severity: str
    title: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    event: Optional[AlertEventInfo] = None

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    """Paginated list of alerts."""
    alerts: List[AlertResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
