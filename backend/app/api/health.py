"""
Health check API endpoint.
"""

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db
from app.core.config import settings

router = APIRouter(tags=["Health"])

# Track application start time
_start_time = time.time()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    System health check: API status, database connectivity, version, uptime.
    This endpoint is intentionally NOT behind authentication.
    """
    # Check database connectivity
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    # Calculate uptime
    uptime_seconds = int(time.time() - _start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "api": "online",
        "database": db_status,
        "version": settings.APP_VERSION,
        "uptime": f"{hours}h {minutes}m {seconds}s",
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
