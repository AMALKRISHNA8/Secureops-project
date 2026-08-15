"""
Detection engine orchestrator.

Runs all registered detection rules against a security event and
creates alerts for any matches.
"""

import logging
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from app.db.models import SecurityEvent, Alert
from app.detection.rules import ALL_RULES
from app.services.alert_service import create_alert

logger = logging.getLogger("secureops.detection")


def run_detection(event: SecurityEvent, db: Session) -> List[Alert]:
    """
    Run all detection rules against the given event.
    Returns a list of Alert objects created for any matched rules.
    """
    alerts: List[Alert] = []

    for rule_fn in ALL_RULES:
        try:
            result = rule_fn(event, db)
            if result and result.get("matched"):
                alert = create_alert(db, event.id, result)
                alerts.append(alert)
                logger.info(
                    "Detection rule '%s' matched event %s (severity: %s)",
                    result["rule_name"],
                    event.id,
                    result["severity"].value if hasattr(result["severity"], "value") else result["severity"],
                )
        except Exception as e:
            # Log the error but don't let one broken rule stop the others
            logger.error(
                "Error running detection rule '%s' on event %s: %s",
                rule_fn.__name__,
                event.id,
                str(e),
            )

    if not alerts:
        logger.debug("No detection rules matched event %s", event.id)

    return alerts
