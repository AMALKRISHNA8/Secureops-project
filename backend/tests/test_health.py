"""
Tests for root and health endpoints.
"""

import pytest


class TestRoot:
    """Tests for GET /"""

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "version" in data
        assert data["message"] == "SecureOps API is running"


class TestHealth:
    """Tests for GET /health"""

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["api"] == "online"
        assert data["database"] == "healthy"
        assert "version" in data
        assert "uptime" in data

    def test_health_no_auth_required(self, client):
        """Health endpoint should work without authentication."""
        response = client.get("/health")
        assert response.status_code == 200


class TestDashboard:
    """Tests for dashboard endpoints."""

    def test_dashboard_stats(self, client, auth_headers):
        response = client.get("/api/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_events" in data
        assert "total_alerts" in data
        assert "critical_alerts" in data

    def test_dashboard_timeline(self, client, auth_headers):
        response = client.get("/api/dashboard/timeline", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "timeline" in data
        assert "severity_distribution" in data
        assert "top_source_ips" in data
        assert "top_event_types" in data

    def test_dashboard_requires_auth(self, client):
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 401
