"""
Tests for the detection engine and rules.
"""

import pytest
from datetime import datetime, timedelta, timezone

from app.db.models import SecurityEvent, SeverityLevel
from app.detection.rules import (
    rule_multiple_failed_logins,
    rule_suspicious_port_activity,
    rule_privilege_escalation,
    rule_suspicious_authentication,
    rule_malware_indicator,
)
from app.services.detection_engine import run_detection


class TestMultipleFailedLogins:
    """Test the multiple failed logins detection rule."""

    def test_triggers_on_threshold(self, test_db):
        """Should trigger when failed login count meets threshold."""
        # Create 3 failed login events from the same IP
        for i in range(3):
            event = SecurityEvent(
                source="auth-server",
                source_ip="192.168.1.50",
                event_type="failed_login",
                description=f"Failed login attempt {i}",
                severity=SeverityLevel.MEDIUM,
                timestamp=datetime.now(timezone.utc),
            )
            test_db.add(event)
        test_db.commit()

        result = rule_multiple_failed_logins(event, test_db)
        assert result is not None
        assert result["matched"] is True
        assert result["severity"] == SeverityLevel.HIGH

    def test_no_trigger_below_threshold(self, test_db):
        """Should not trigger below the threshold."""
        event = SecurityEvent(
            source="auth-server",
            source_ip="10.0.0.1",
            event_type="failed_login",
            description="Single failed attempt",
            severity=SeverityLevel.MEDIUM,
            timestamp=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()

        result = rule_multiple_failed_logins(event, test_db)
        assert result is None

    def test_ignores_non_failed_login(self, test_db):
        """Should not trigger for non-failed-login events."""
        event = SecurityEvent(
            source="auth-server",
            source_ip="192.168.1.50",
            event_type="successful_login",
            severity=SeverityLevel.LOW,
            timestamp=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()

        result = rule_multiple_failed_logins(event, test_db)
        assert result is None


class TestSuspiciousPortActivity:
    """Test the suspicious port activity detection rule."""

    def test_triggers_on_port_scan(self, test_db):
        event = SecurityEvent(
            source="network-monitor",
            source_ip="192.168.1.105",
            event_type="port_scan",
            description="Port scan detected",
            severity=SeverityLevel.MEDIUM,
            timestamp=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()

        result = rule_suspicious_port_activity(event, test_db)
        assert result is not None
        assert result["severity"] == SeverityLevel.MEDIUM

    def test_triggers_on_suspicious_port_in_raw_data(self, test_db):
        event = SecurityEvent(
            source="firewall",
            source_ip="10.0.0.5",
            event_type="connection_log",
            description="Outbound connection",
            severity=SeverityLevel.LOW,
            raw_data={"port": 4444},
            timestamp=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()

        result = rule_suspicious_port_activity(event, test_db)
        assert result is not None


class TestPrivilegeEscalation:
    """Test the privilege escalation detection rule."""

    def test_triggers_on_escalation_keyword(self, test_db):
        event = SecurityEvent(
            source="endpoint-security",
            source_ip="192.168.2.30",
            event_type="system_event",
            description="Privilege escalation attempt detected on server",
            severity=SeverityLevel.HIGH,
            timestamp=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()

        result = rule_privilege_escalation(event, test_db)
        assert result is not None
        assert result["severity"] == SeverityLevel.CRITICAL

    def test_no_trigger_on_normal_event(self, test_db):
        event = SecurityEvent(
            source="auth-server",
            source_ip="10.0.0.1",
            event_type="successful_login",
            description="Normal user login",
            severity=SeverityLevel.LOW,
            timestamp=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()

        result = rule_privilege_escalation(event, test_db)
        assert result is None


class TestSuspiciousAuthentication:
    """Test the suspicious authentication detection rule."""

    def test_triggers_on_impossible_travel(self, test_db):
        event = SecurityEvent(
            source="auth-server",
            source_ip="172.16.0.100",
            event_type="suspicious_login",
            description="Impossible travel detected",
            severity=SeverityLevel.HIGH,
            timestamp=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()

        result = rule_suspicious_authentication(event, test_db)
        assert result is not None
        assert result["severity"] == SeverityLevel.HIGH


class TestMalwareIndicator:
    """Test the malware indicator detection rule."""

    def test_triggers_on_malware_keyword(self, test_db):
        event = SecurityEvent(
            source="antivirus-engine",
            source_ip="192.168.3.42",
            event_type="malware_detected",
            description="Test malware signature detected",
            severity=SeverityLevel.CRITICAL,
            timestamp=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()

        result = rule_malware_indicator(event, test_db)
        assert result is not None
        assert result["severity"] == SeverityLevel.CRITICAL

    def test_triggers_on_raw_data_indicator(self, test_db):
        event = SecurityEvent(
            source="endpoint",
            source_ip="192.168.3.42",
            event_type="file_scan",
            description="File scan completed",
            severity=SeverityLevel.LOW,
            raw_data={"signature": "test_malware_signature"},
            timestamp=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()

        result = rule_malware_indicator(event, test_db)
        assert result is not None


class TestDetectionEngine:
    """Test the detection engine orchestrator."""

    def test_engine_creates_alerts(self, client, auth_headers):
        """Submit an event that triggers detection and verify alerts are created."""
        response = client.post(
            "/api/events",
            json={
                "source": "antivirus-engine",
                "source_ip": "192.168.3.42",
                "event_type": "malware_detected",
                "description": "Malware detected in uploaded file (test_malware_signature)",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["alerts_generated"] > 0

    def test_engine_no_alerts_for_benign_event(self, client, auth_headers):
        """Submit a benign event and verify no alerts are generated."""
        response = client.post(
            "/api/events",
            json={
                "source": "auth-server",
                "source_ip": "10.0.0.25",
                "event_type": "successful_login",
                "description": "User logged in successfully",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["alerts_generated"] == 0
