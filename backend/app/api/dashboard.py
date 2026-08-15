"""
Dashboard statistics API endpoints.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.db.models import (
    SecurityEvent,
    Alert,
    SeverityLevel,
    AlertStatus,
    User,
)
from app.core.security import get_current_user
from app.schemas.dashboard import (
    DashboardStats,
    DashboardTimeline,
    TimelineEntry,
    SeverityCount,
    TopSourceIP,
    TopEventType,
)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get aggregate security statistics for the dashboard."""
    total_events = db.query(SecurityEvent).count()
    total_alerts = db.query(Alert).count()

    # Alerts by severity
    critical_alerts = (
        db.query(Alert).filter(Alert.severity == SeverityLevel.CRITICAL).count()
    )
    high_alerts = (
        db.query(Alert).filter(Alert.severity == SeverityLevel.HIGH).count()
    )
    medium_alerts = (
        db.query(Alert).filter(Alert.severity == SeverityLevel.MEDIUM).count()
    )
    low_alerts = (
        db.query(Alert).filter(Alert.severity == SeverityLevel.LOW).count()
    )

    # Alerts by status
    open_alerts = (
        db.query(Alert).filter(Alert.status == AlertStatus.OPEN).count()
    )
    investigating_alerts = (
        db.query(Alert).filter(Alert.status == AlertStatus.INVESTIGATING).count()
    )
    resolved_alerts = (
        db.query(Alert).filter(Alert.status == AlertStatus.RESOLVED).count()
    )

    # Events today
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    events_today = (
        db.query(SecurityEvent)
        .filter(SecurityEvent.timestamp >= today_start)
        .count()
    )

    return DashboardStats(
        total_events=total_events,
        total_alerts=total_alerts,
        critical_alerts=critical_alerts,
        high_alerts=high_alerts,
        medium_alerts=medium_alerts,
        low_alerts=low_alerts,
        open_alerts=open_alerts,
        investigating_alerts=investigating_alerts,
        resolved_alerts=resolved_alerts,
        events_today=events_today,
    )


@router.get("/timeline", response_model=DashboardTimeline)
def get_dashboard_timeline(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get timeline data, severity distribution, top IPs, and top event types."""

    # --- Timeline: events per day for the last 30 days ---
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)

    events_in_range = (
        db.query(SecurityEvent)
        .filter(SecurityEvent.timestamp >= thirty_days_ago)
        .all()
    )

    # Build daily counts
    day_counts: dict[str, int] = {}
    for i in range(30):
        day = (thirty_days_ago + timedelta(days=i)).strftime("%Y-%m-%d")
        day_counts[day] = 0

    for event in events_in_range:
        day_key = event.timestamp.strftime("%Y-%m-%d")
        if day_key in day_counts:
            day_counts[day_key] += 1

    timeline = [
        TimelineEntry(date=date, count=count)
        for date, count in sorted(day_counts.items())
    ]

    # --- Severity distribution ---
    severity_rows = (
        db.query(SecurityEvent.severity, func.count(SecurityEvent.id))
        .group_by(SecurityEvent.severity)
        .all()
    )
    severity_distribution = [
        SeverityCount(
            severity=row[0].value if hasattr(row[0], "value") else str(row[0]),
            count=row[1],
        )
        for row in severity_rows
    ]

    # --- Top source IPs ---
    ip_rows = (
        db.query(SecurityEvent.source_ip, func.count(SecurityEvent.id))
        .filter(SecurityEvent.source_ip.isnot(None))
        .group_by(SecurityEvent.source_ip)
        .order_by(func.count(SecurityEvent.id).desc())
        .limit(10)
        .all()
    )
    top_source_ips = [
        TopSourceIP(source_ip=row[0], count=row[1]) for row in ip_rows
    ]

    # --- Top event types ---
    type_rows = (
        db.query(SecurityEvent.event_type, func.count(SecurityEvent.id))
        .group_by(SecurityEvent.event_type)
        .order_by(func.count(SecurityEvent.id).desc())
        .limit(10)
        .all()
    )
    top_event_types = [
        TopEventType(event_type=row[0], count=row[1]) for row in type_rows
    ]

    return DashboardTimeline(
        timeline=timeline,
        severity_distribution=severity_distribution,
        top_source_ips=top_source_ips,
        top_event_types=top_event_types,
    )
