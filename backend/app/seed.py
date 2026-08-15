"""
Seed demo data for local development.

Creates:
- Demo analyst account: analyst / SecureOps2024!
- Demo admin account: admin / SecureOpsAdmin2024!
- Sample security events with detection engine processing
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
import random

from app.db.database import SessionLocal
from app.db.models import User, SecurityEvent, UserRole, SeverityLevel
from app.core.security import hash_password
from app.detection.severity import classify_severity
from app.services.detection_engine import run_detection

logger = logging.getLogger("secureops.seed")

# Sample security events for demonstration
SAMPLE_EVENTS = [
    {
        "source": "auth-server",
        "source_ip": "192.168.1.50",
        "destination_ip": "192.168.1.10",
        "event_type": "failed_login",
        "description": "Multiple failed authentication attempts detected from workstation",
        "raw_data": {"username": "jdoe", "attempts": 5},
    },
    {
        "source": "auth-server",
        "source_ip": "192.168.1.50",
        "destination_ip": "192.168.1.10",
        "event_type": "failed_login",
        "description": "Failed login attempt with invalid credentials",
        "raw_data": {"username": "admin", "reason": "invalid_password"},
    },
    {
        "source": "auth-server",
        "source_ip": "192.168.1.50",
        "destination_ip": "192.168.1.10",
        "event_type": "failed_login",
        "description": "Authentication failure - account lockout threshold approaching",
        "raw_data": {"username": "admin", "attempts": 4},
    },
    {
        "source": "auth-server",
        "source_ip": "10.0.0.25",
        "destination_ip": "10.0.0.1",
        "event_type": "successful_login",
        "description": "User authenticated successfully",
        "raw_data": {"username": "analyst01", "method": "password"},
    },
    {
        "source": "auth-server",
        "source_ip": "172.16.0.100",
        "destination_ip": "172.16.0.1",
        "event_type": "suspicious_login",
        "description": "Impossible travel detected - login from different geographic locations within short timeframe",
        "raw_data": {"username": "svc_account", "location1": "New York", "location2": "London", "time_diff_minutes": 15},
    },
    {
        "source": "network-monitor",
        "source_ip": "192.168.1.105",
        "destination_ip": "192.168.1.1",
        "event_type": "port_scan",
        "description": "Port scan detected - multiple connection attempts to restricted ports",
        "raw_data": {"ports_scanned": [22, 23, 445, 3389], "duration_seconds": 30},
    },
    {
        "source": "network-monitor",
        "source_ip": "10.0.1.55",
        "destination_ip": "10.0.1.200",
        "event_type": "port_activity",
        "description": "Unusual port activity detected on restricted service port",
        "raw_data": {"port": 4444, "protocol": "TCP", "bytes_transferred": 1024},
    },
    {
        "source": "endpoint-security",
        "source_ip": "192.168.2.30",
        "destination_ip": "192.168.2.1",
        "event_type": "privilege_escalation",
        "description": "Privilege escalation attempt detected - unauthorized admin action on server",
        "raw_data": {"user": "guest_user", "attempted_action": "modify_system_config"},
    },
    {
        "source": "endpoint-security",
        "source_ip": "10.0.2.15",
        "destination_ip": "10.0.2.1",
        "event_type": "privilege_change",
        "description": "User role changed from standard to admin without authorization workflow",
        "raw_data": {"user": "temp_contractor", "old_role": "user", "new_role": "admin"},
    },
    {
        "source": "antivirus-engine",
        "source_ip": "192.168.3.42",
        "destination_ip": None,
        "event_type": "malware_detected",
        "description": "Test malware signature detected in uploaded file (test_malware_signature)",
        "raw_data": {"filename": "test_sample.exe", "signature": "test_malware_signature", "action": "quarantined"},
    },
    {
        "source": "firewall",
        "source_ip": "172.16.1.80",
        "destination_ip": "172.16.1.1",
        "event_type": "network_anomaly",
        "description": "Unusual outbound traffic pattern detected",
        "raw_data": {"bytes_out": 500000, "destination": "external", "protocol": "HTTPS"},
    },
    {
        "source": "siem-collector",
        "source_ip": "192.168.1.200",
        "destination_ip": "192.168.1.10",
        "event_type": "policy_violation",
        "description": "Security policy violation - unauthorized software installation attempt",
        "raw_data": {"software": "remote_tool_v2", "user": "intern01"},
    },
    {
        "source": "auth-server",
        "source_ip": "10.0.3.50",
        "destination_ip": "10.0.3.1",
        "event_type": "successful_login",
        "description": "Admin user authenticated via MFA",
        "raw_data": {"username": "sec_admin", "method": "mfa", "mfa_type": "totp"},
    },
    {
        "source": "endpoint-security",
        "source_ip": "192.168.4.12",
        "destination_ip": "192.168.4.1",
        "event_type": "configuration_change",
        "description": "Firewall rule modified - new outbound rule added",
        "raw_data": {"rule": "allow_outbound_8443", "modified_by": "net_admin"},
    },
    {
        "source": "log-aggregator",
        "source_ip": "10.0.0.100",
        "destination_ip": None,
        "event_type": "system_error",
        "description": "Application crash detected in monitoring service",
        "raw_data": {"service": "log-collector", "error": "out_of_memory", "restart": True},
    },
    {
        "source": "auth-server",
        "source_ip": "192.168.1.75",
        "destination_ip": "192.168.1.10",
        "event_type": "failed_login",
        "description": "Brute force attempt detected from external-facing workstation",
        "raw_data": {"username": "root", "attempts": 12},
    },
    {
        "source": "network-monitor",
        "source_ip": "172.16.2.30",
        "destination_ip": "172.16.2.1",
        "event_type": "port_scan",
        "description": "Service probe detected targeting database ports",
        "raw_data": {"ports_scanned": [1433, 3306, 5432], "source_country": "unknown"},
    },
    {
        "source": "endpoint-security",
        "source_ip": "192.168.5.60",
        "destination_ip": "192.168.5.1",
        "event_type": "unauthorized_access",
        "description": "Unauthorized access attempt to restricted file share",
        "raw_data": {"share": "\\\\fileserver\\confidential", "user": "guest"},
    },
    {
        "source": "auth-server",
        "source_ip": "10.0.4.22",
        "destination_ip": "10.0.4.1",
        "event_type": "suspicious_login",
        "description": "Credential stuffing detected - multiple accounts targeted from single IP",
        "raw_data": {"accounts_targeted": 15, "successful": 1, "duration_minutes": 5},
    },
    {
        "source": "antivirus-engine",
        "source_ip": "192.168.6.18",
        "destination_ip": None,
        "event_type": "malware_detected",
        "description": "Malware detected in email attachment (malware_detected indicator)",
        "raw_data": {"filename": "invoice.pdf.exe", "signature": "malware_detected", "action": "blocked"},
    },
    {
        "source": "firewall",
        "source_ip": "172.16.3.45",
        "destination_ip": "172.16.3.1",
        "event_type": "network_anomaly",
        "description": "DNS tunneling attempt detected",
        "raw_data": {"query_count": 500, "unique_domains": 450, "time_window_minutes": 10},
    },
    {
        "source": "auth-server",
        "source_ip": "192.168.7.33",
        "destination_ip": "192.168.7.1",
        "event_type": "successful_login",
        "description": "Standard user login during business hours",
        "raw_data": {"username": "user_smith", "method": "sso"},
    },
    {
        "source": "siem-collector",
        "source_ip": "10.0.5.88",
        "destination_ip": "10.0.5.1",
        "event_type": "policy_violation",
        "description": "Data loss prevention alert - sensitive data in outbound email",
        "raw_data": {"policy": "PII_detection", "action": "blocked", "recipient": "external@example.com"},
    },
    {
        "source": "endpoint-security",
        "source_ip": "192.168.8.90",
        "destination_ip": "192.168.8.1",
        "event_type": "privilege_escalation",
        "description": "Sudo abuse detected - user escalated to root without approval",
        "raw_data": {"user": "developer01", "command": "sudo su -", "approved": False},
    },
    {
        "source": "network-monitor",
        "source_ip": "172.16.4.15",
        "destination_ip": "172.16.4.100",
        "event_type": "port_activity",
        "description": "Connection attempt to known C2 port detected",
        "raw_data": {"port": 31337, "protocol": "TCP", "direction": "outbound"},
    },
]


def seed_demo_data():
    """Seed the database with demo users and sample security events."""
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            logger.info("Database already seeded, skipping")
            return

        logger.info("Seeding demo data...")

        # Create demo users
        analyst_user = User(
            username="analyst",
            email="analyst@secureops.local",
            password_hash=hash_password("SecureOps2024!"),
            role=UserRole.ANALYST,
        )
        admin_user = User(
            username="admin",
            email="admin@secureops.local",
            password_hash=hash_password("SecureOpsAdmin2024!"),
            role=UserRole.ADMIN,
        )
        db.add(analyst_user)
        db.add(admin_user)
        db.commit()
        logger.info("Demo users created (analyst, admin)")

        # Create sample events spread over the last 14 days
        now = datetime.now(timezone.utc)
        for i, event_data in enumerate(SAMPLE_EVENTS):
            # Spread events over the past 14 days
            hours_ago = random.randint(1, 14 * 24)
            event_time = now - timedelta(hours=hours_ago)

            severity = classify_severity(
                event_data["event_type"],
                event_data.get("severity"),
            )

            event = SecurityEvent(
                source=event_data["source"],
                source_ip=event_data.get("source_ip"),
                destination_ip=event_data.get("destination_ip"),
                event_type=event_data["event_type"],
                description=event_data.get("description"),
                severity=severity,
                raw_data=event_data.get("raw_data"),
                timestamp=event_time,
            )
            db.add(event)
            db.commit()
            db.refresh(event)

            # Run detection engine on each seeded event
            run_detection(event, db)

        logger.info("Seeded %d sample security events", len(SAMPLE_EVENTS))
        logger.info("Demo data seeding complete")

    except Exception as e:
        logger.error("Error seeding demo data: %s", str(e))
        db.rollback()
    finally:
        db.close()
