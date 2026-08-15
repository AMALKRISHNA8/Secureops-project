"""
Severity classification for security events.
"""

from app.db.models import SeverityLevel


# Map event types to default severity levels
EVENT_TYPE_SEVERITY_MAP = {
    "successful_login": SeverityLevel.LOW,
    "failed_login": SeverityLevel.MEDIUM,
    "suspicious_login": SeverityLevel.HIGH,
    "privilege_change": SeverityLevel.HIGH,
    "privilege_escalation": SeverityLevel.CRITICAL,
    "port_scan": SeverityLevel.MEDIUM,
    "port_activity": SeverityLevel.MEDIUM,
    "malware_detected": SeverityLevel.CRITICAL,
    "data_exfiltration": SeverityLevel.CRITICAL,
    "unauthorized_access": SeverityLevel.HIGH,
    "brute_force": SeverityLevel.HIGH,
    "policy_violation": SeverityLevel.MEDIUM,
    "system_error": SeverityLevel.LOW,
    "configuration_change": SeverityLevel.MEDIUM,
    "network_anomaly": SeverityLevel.MEDIUM,
}


def classify_severity(event_type: str, provided_severity: str = None) -> SeverityLevel:
    """
    Determine severity for an event.
    If a valid severity is explicitly provided, use it.
    Otherwise, fall back to the event type mapping, defaulting to LOW.
    """
    if provided_severity:
        try:
            return SeverityLevel(provided_severity.lower())
        except ValueError:
            pass

    return EVENT_TYPE_SEVERITY_MAP.get(event_type.lower(), SeverityLevel.LOW)
