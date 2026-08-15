"""
Security events API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.core.security import get_current_user
from app.schemas.event import (
    EventCreate,
    EventResponse,
    EventListResponse,
    EventCreateResponse,
)
from app.services import event_service
from app.services.detection_engine import run_detection

router = APIRouter(prefix="/api/events", tags=["Security Events"])


@router.get("", response_model=EventListResponse)
def list_events(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str = Query(None, description="Search in description, source, IP, type"),
    severity: str = Query(None, description="Filter by severity: low/medium/high/critical"),
    event_type: str = Query(None, description="Filter by event type"),
    event_status: str = Query(None, alias="status", description="Filter by status"),
    source_ip: str = Query(None, description="Filter by source IP"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List security events with optional search, filtering, and pagination."""
    events, total = event_service.list_events(
        db,
        page=page,
        page_size=page_size,
        search=search,
        severity=severity,
        event_type=event_type,
        status=event_status,
        source_ip=source_ip,
    )

    return EventListResponse(
        events=[EventResponse.model_validate(e) for e in events],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=event_service.calculate_total_pages(total, page_size),
    )


@router.post("", response_model=EventCreateResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a new security event.
    The event is automatically processed through the detection engine.
    """
    # Create the event
    event = event_service.create_event(db, event_data)

    # Run detection engine
    alerts = run_detection(event, db)

    # Refresh event to include alerts relationship
    db.refresh(event)

    return EventCreateResponse(
        event=EventResponse.model_validate(event),
        alerts_generated=len(alerts),
    )


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific security event by ID, including associated alerts."""
    event = event_service.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return EventResponse.model_validate(event)
