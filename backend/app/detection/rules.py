"""
Detection rules for the SecureOps threat detection engine.

Each rule is a function that receives a security event (ORM model) and
a database session, and returns a detection result dict if the rule matches,
or None if it does not.

Detection result format:
{
    "matched": True,
    "rule_name": str,
    "severity": SeverityLevel,
    "title": str,
    "description": str,
}
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List

from sqlalchemy.orm import Session

from app.db.models import SecurityEvent, SeverityLevel


# --- Rule 1: Multiple Failed Logins ---

FAILED_LOGIN_THRESHOLD = 3
FAILED_LOGIN_WINDOW_MINUTES = 10


def rule_multiple_failed_logins(
    event: SecurityEvent, db: Session
) -> Optional[Dict[str, Any]]:
    """
    Detect repeated failed authentication events from the same source IP
    within a configurable time window.
    """
    if event.event_type != "failed_login":
        return None

    if not event.source_ip:
        return None

    window_start = datetime.now(timezone.utc) - timedelta(
        minutes=FAILED_LOGIN_WINDOW_MINUTES
    )

    failed_count = (
        db.query(SecurityEvent)
        .filter(
            SecurityEvent.source_ip == event.source_ip,
            SecurityEvent.event_type == "failed_login",
            SecurityEvent.timestamp >= window_start,
        )
        .count()
    )

    if failed_count >= FAILED_LOGIN_THRESHOLD:
        return {
            "matched": True,
            "rule_name": "multiple_failed_logins",
            "severity": SeverityLevel.HIGH,
            "title": f"Multiple Failed Login Attempts from {event.source_ip}",
            "description": (
                f"Detected {failed_count} failed login attempts from "
                f"IP {event.source_ip} within the last "
                f"{FAILED_LOGIN_WINDOW_MINUTES} minutes. "
                f"This may indicate a brute-force attack."
            ),
        }

    return None


# --- Rule 2: Suspicious Port Activity ---

SUSPICIOUS_PORTS = {
    22, 23, 445, 1433, 3306, 3389, 5432, 5900, 8080, 8443, 4444, 1234, 31337,
}

PORT_KEYWORDS = [
    "port_scan", "port scan", "unusual port", "restricted port",
    "connection attempt", "service probe",
]


def rule_suspicious_port_activity(
    event: SecurityEvent, db: Session
) -> Optional[Dict[str, Any]]:
    """
    Detect events indicating repeated connection attempts toward unusual
    or restricted service ports.
    """
    description_lower = (event.description or "").lower()
    event_type_lower = (event.event_type or "").lower()

    # Check for port-related keywords in description or event type
    keyword_match = any(
        kw in description_lower or kw in event_type_lower for kw in PORT_KEYWORDS
    )

    # Check for suspicious ports in raw_data
    port_match = False
    if event.raw_data and isinstance(event.raw_data, dict):
        port = event.raw_data.get("port") or event.raw_data.get("destination_port")
        if port and int(port) in SUSPICIOUS_PORTS:
            port_match = True

    if event_type_lower in ("port_scan", "port_activity") or keyword_match or port_match:
        return {
            "matched": True,
            "rule_name": "suspicious_port_activity",
            "severity": SeverityLevel.MEDIUM,
            "title": f"Suspicious Port Activity Detected",
            "description": (
                f"Event from {event.source_ip or 'unknown'} indicates "
                f"suspicious port activity. Event type: {event.event_type}. "
                f"This may indicate port scanning or unauthorized service access."
            ),
        }

    return None


# --- Rule 3: Privilege Escalation ---

PRIVILEGE_KEYWORDS = [
    "privilege escalation", "privilege_escalation",
    "unauthorized admin", "admin escalation",
    "unexpected privilege", "privilege change",
    "root access", "sudo abuse", "elevation of privilege",
]


def rule_privilege_escalation(
    event: SecurityEvent, db: Session
) -> Optional[Dict[str, Any]]:
    """
    Detect log events containing indicators of privilege escalation.
    """
    description_lower = (event.description or "").lower()
    event_type_lower = (event.event_type or "").lower()

    match = any(
        kw in description_lower or kw in event_type_lower for kw in PRIVILEGE_KEYWORDS
    )

    if match or event_type_lower == "privilege_escalation":
        return {
            "matched": True,
            "rule_name": "privilege_escalation",
            "severity": SeverityLevel.CRITICAL,
            "title": f"Privilege Escalation Detected",
            "description": (
                f"Potential privilege escalation event from "
                f"{event.source_ip or 'unknown source'}. "
                f"Description: {event.description or 'N/A'}. "
                f"Immediate investigation recommended."
            ),
        }

    return None


# --- Rule 4: Suspicious Authentication ---

SUSPICIOUS_AUTH_KEYWORDS = [
    "impossible travel", "impossible login",
    "concurrent session", "simultaneous login",
    "suspicious account", "account compromise",
    "credential stuffing", "anomalous login",
]


def rule_suspicious_authentication(
    event: SecurityEvent, db: Session
) -> Optional[Dict[str, Any]]:
    """
    Detect unusual authentication behavior such as impossible login patterns,
    repeated failures, or suspicious account activity.
    """
    description_lower = (event.description or "").lower()
    event_type_lower = (event.event_type or "").lower()

    # Check for suspicious auth keywords
    keyword_match = any(
        kw in description_lower or kw in event_type_lower
        for kw in SUSPICIOUS_AUTH_KEYWORDS
    )

    # Check for suspicious_login event type
    if keyword_match or event_type_lower == "suspicious_login":
        return {
            "matched": True,
            "rule_name": "suspicious_authentication",
            "severity": SeverityLevel.HIGH,
            "title": f"Suspicious Authentication Activity",
            "description": (
                f"Unusual authentication behavior detected from "
                f"{event.source_ip or 'unknown'}. "
                f"Event type: {event.event_type}. "
                f"This may indicate credential compromise or account takeover."
            ),
        }

    return None


# --- Rule 5: Malware Indicator ---

MALWARE_INDICATORS = [
    "malware_detected", "test_malware_signature",
    "malware detected", "virus detected",
    "trojan detected", "ransomware detected",
]


def rule_malware_indicator(
    event: SecurityEvent, db: Session
) -> Optional[Dict[str, Any]]:
    """
    Detect security events containing known safe-to-test malware indicators.
    Does NOT implement real malware detection.
    """
    description_lower = (event.description or "").lower()
    event_type_lower = (event.event_type or "").lower()

    match = any(
        indicator in description_lower or indicator in event_type_lower
        for indicator in MALWARE_INDICATORS
    )

    # Also check raw_data for indicators
    if not match and event.raw_data and isinstance(event.raw_data, dict):
        raw_str = str(event.raw_data).lower()
        match = any(indicator in raw_str for indicator in MALWARE_INDICATORS)

    if match:
        return {
            "matched": True,
            "rule_name": "malware_indicator",
            "severity": SeverityLevel.CRITICAL,
            "title": f"Malware Indicator Detected",
            "description": (
                f"A malware-related indicator was detected in an event from "
                f"{event.source_ip or 'unknown'}. "
                f"Event type: {event.event_type}. "
                f"This is a test indicator for demonstration purposes."
            ),
        }

    return None


# --- Rule Registry ---

ALL_RULES = [
    rule_multiple_failed_logins,
    rule_suspicious_port_activity,
    rule_privilege_escalation,
    rule_suspicious_authentication,
    rule_malware_indicator,
]
