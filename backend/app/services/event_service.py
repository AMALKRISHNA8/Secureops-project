"""
Service layer for security event operations.
"""

import math
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models import SecurityEvent, SeverityLevel, EventStatus
from app.schemas.event import EventCreate
from app.detection.severity import classify_severity


def create_event(db: Session, event_data: EventCreate) -> SecurityEvent:
    """Create and persist a new security event with auto-classified severity."""
    severity = classify_severity(
        event_data.event_type,
        event_data.severity,
    )

    event = SecurityEvent(
        source=event_data.source,
        source_ip=event_data.source_ip,
        destination_ip=event_data.destination_ip,
        event_type=event_data.event_type,
        description=event_data.description,
        severity=severity,
        raw_data=event_data.raw_data,
        timestamp=datetime.now(timezone.utc),
    )

    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_event_by_id(db: Session, event_id: str) -> Optional[SecurityEvent]:
    """Retrieve a single event by ID."""
    return db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()


def list_events(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    source_ip: Optional[str] = None,
) -> Tuple[List[SecurityEvent], int]:
    """
    List events with optional filtering, search, and pagination.
    Returns (events, total_count).
    """
    query = db.query(SecurityEvent)

    # Apply filters
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            SecurityEvent.description.ilike(search_pattern)
            | SecurityEvent.source.ilike(search_pattern)
            | SecurityEvent.source_ip.ilike(search_pattern)
            | SecurityEvent.event_type.ilike(search_pattern)
        )

    if severity:
        try:
            sev = SeverityLevel(severity.lower())
            query = query.filter(SecurityEvent.severity == sev)
        except ValueError:
            pass

    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type)

    if status:
        try:
            st = EventStatus(status.lower())
            query = query.filter(SecurityEvent.status == st)
        except ValueError:
            pass

    if source_ip:
        query = query.filter(SecurityEvent.source_ip == source_ip)

    # Total count before pagination
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    events = (
        query.order_by(desc(SecurityEvent.timestamp))
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return events, total


def calculate_total_pages(total: int, page_size: int) -> int:
    """Calculate the total number of pages."""
    return max(1, math.ceil(total / page_size))
