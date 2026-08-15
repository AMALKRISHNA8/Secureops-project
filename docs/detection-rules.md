# Detection Rules Documentation

SecureOps includes a modular, rule-based threat detection engine. Each rule evaluates incoming security events and generates alerts when suspicious activity is detected.

## Rule Architecture

Every detection rule follows this interface:
- **Input**: A `SecurityEvent` ORM object + database session
- **Output**: A detection result dictionary (or `None` if no match)

```python
{
    "matched": True,
    "rule_name": "rule_identifier",
    "severity": SeverityLevel.HIGH,
    "title": "Human-readable alert title",
    "description": "Detailed description of the detected threat"
}
```

---

## Rule 1: Multiple Failed Logins

**Identifier**: `multiple_failed_logins`  
**Severity**: HIGH  

**Description**: Detects repeated failed authentication events from the same source IP within a configurable time window.

**Trigger conditions**:
- Event type is `failed_login`
- Source IP has ≥ 3 failed login events in the last 10 minutes

**Configuration**:
- `FAILED_LOGIN_THRESHOLD = 3`
- `FAILED_LOGIN_WINDOW_MINUTES = 10`

**Example**: Three failed login attempts from `192.168.1.50` within 10 minutes will trigger this rule.

---

## Rule 2: Suspicious Port Activity

**Identifier**: `suspicious_port_activity`  
**Severity**: MEDIUM  

**Description**: Detects events indicating connection attempts toward unusual or restricted service ports.

**Trigger conditions**:
- Event type is `port_scan` or `port_activity`
- Description contains port-related keywords (e.g., "port scan", "restricted port")
- Raw data contains a suspicious port number (22, 23, 445, 3389, 4444, 31337, etc.)

**Monitored ports**: 22, 23, 445, 1433, 3306, 3389, 5432, 5900, 8080, 8443, 4444, 1234, 31337

---

## Rule 3: Privilege Escalation

**Identifier**: `privilege_escalation`  
**Severity**: CRITICAL  

**Description**: Detects log events containing indicators of privilege escalation or unauthorized admin actions.

**Trigger conditions**:
- Event type is `privilege_escalation`
- Description contains keywords: "privilege escalation", "unauthorized admin", "sudo abuse", "elevation of privilege", "root access", etc.

---

## Rule 4: Suspicious Authentication

**Identifier**: `suspicious_authentication`  
**Severity**: HIGH  

**Description**: Detects unusual authentication behavior such as impossible login patterns, concurrent sessions, or credential stuffing.

**Trigger conditions**:
- Event type is `suspicious_login`
- Description contains keywords: "impossible travel", "concurrent session", "credential stuffing", "anomalous login", etc.

---

## Rule 5: Malware Indicator

**Identifier**: `malware_indicator`  
**Severity**: CRITICAL  

**Description**: Detects security events containing known safe-to-test malware indicators. This does NOT implement real malware detection.

**Trigger conditions**:
- Event type is `malware_detected`
- Description or raw data contains: "malware_detected", "test_malware_signature", "virus detected", etc.

---

## Severity Levels

| Level | Color | Description |
|-------|-------|-------------|
| LOW | Green | Informational events, normal activity |
| MEDIUM | Amber | Potentially suspicious, warrants review |
| HIGH | Orange | Likely malicious, requires investigation |
| CRITICAL | Red | Confirmed threat, immediate action needed |

## Adding New Rules

1. Create a new function in `backend/app/detection/rules.py`
2. Follow the standard signature: `def rule_name(event, db) -> Optional[Dict]`
3. Add the function to the `ALL_RULES` list
4. The detection engine will automatically pick it up
