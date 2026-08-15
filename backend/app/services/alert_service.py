"""
Service layer for alert operations.
"""

import math
from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models import Alert, AlertStatus, SeverityLevel


def create_alert(
    db: Session, event_id: str, detection_result: Dict[str, Any]
) -> Alert:
    """Create an alert from a detection rule result."""
    alert = Alert(
        event_id=event_id,
        rule_name=detection_result["rule_name"],
        severity=detection_result["severity"],
        title=detection_result["title"],
        description=detection_result["description"],
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_alert_by_id(db: Session, alert_id: str) -> Optional[Alert]:
    """Retrieve a single alert by ID."""
    return db.query(Alert).filter(Alert.id == alert_id).first()


def list_alerts(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    severity: Optional[str] = None,
    status: Optional[str] = None,
) -> Tuple[List[Alert], int]:
    """List alerts with optional filtering and pagination."""
    query = db.query(Alert)

    if severity:
        try:
            sev = SeverityLevel(severity.lower())
            query = query.filter(Alert.severity == sev)
        except ValueError:
            pass

    if status:
        try:
            st = AlertStatus(status.lower())
            query = query.filter(Alert.status == st)
        except ValueError:
            pass

    total = query.count()

    offset = (page - 1) * page_size
    alerts = (
        query.order_by(desc(Alert.created_at))
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return alerts, total


def update_alert_status(
    db: Session, alert_id: str, new_status: str
) -> Optional[Alert]:
    """Update an alert's status. Sets resolved_at when status becomes 'resolved'."""
    alert = get_alert_by_id(db, alert_id)
    if not alert:
        return None

    try:
        alert.status = AlertStatus(new_status.lower())
    except ValueError:
        return None

    if alert.status == AlertStatus.RESOLVED:
        alert.resolved_at = datetime.now(timezone.utc)
    else:
        alert.resolved_at = None

    db.commit()
    db.refresh(alert)
    return alert


def calculate_total_pages(total: int, page_size: int) -> int:
    """Calculate the total number of pages."""
    return max(1, math.ceil(total / page_size))
