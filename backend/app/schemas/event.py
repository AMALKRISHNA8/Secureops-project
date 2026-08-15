"""
Pydantic schemas for security event endpoints.
"""

from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    """Schema for submitting a new security event."""
    source: str = Field(..., min_length=1, max_length=100)
    source_ip: Optional[str] = Field(None, max_length=45)
    destination_ip: Optional[str] = Field(None, max_length=45)
    event_type: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    severity: Optional[str] = Field(None, pattern=r"^(low|medium|high|critical)$")
    raw_data: Optional[Dict[str, Any]] = None


class AlertInEvent(BaseModel):
    """Nested alert info when returning an event."""
    id: str
    rule_name: str
    severity: str
    title: str
    description: Optional[str] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class EventResponse(BaseModel):
    """Schema for a single security event response."""
    id: str
    timestamp: datetime
    source: str
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    event_type: str
    description: Optional[str] = None
    severity: str
    status: str
    raw_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    alerts: List[AlertInEvent] = []

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    """Paginated list of events."""
    events: List[EventResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class EventCreateResponse(BaseModel):
    """Response after creating an event, includes generated alerts."""
    event: EventResponse
    alerts_generated: int
