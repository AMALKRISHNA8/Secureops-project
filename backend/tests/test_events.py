"""
Tests for security event endpoints.
"""

import pytest


class TestCreateEvent:
    """Tests for POST /api/events"""

    def test_create_event(self, client, auth_headers):
        response = client.post(
            "/api/events",
            json={
                "source": "auth-server",
                "source_ip": "192.168.1.50",
                "destination_ip": "192.168.1.10",
                "event_type": "failed_login",
                "description": "Failed authentication attempt",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert "event" in data
        assert data["event"]["source"] == "auth-server"
        assert data["event"]["event_type"] == "failed_login"
        assert "alerts_generated" in data

    def test_create_event_unauthenticated(self, client):
        response = client.post(
            "/api/events",
            json={
                "source": "test",
                "event_type": "test_event",
            },
        )
        assert response.status_code == 401

    def test_create_event_auto_severity(self, client, auth_headers):
        response = client.post(
            "/api/events",
            json={
                "source": "antivirus-engine",
                "event_type": "malware_detected",
                "description": "Test malware signature detected",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["event"]["severity"] == "critical"

    def test_create_event_with_raw_data(self, client, auth_headers):
        response = client.post(
            "/api/events",
            json={
                "source": "firewall",
                "source_ip": "10.0.0.5",
                "event_type": "network_anomaly",
                "raw_data": {"bytes_out": 500000, "protocol": "TCP"},
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["event"]["raw_data"]["bytes_out"] == 500000


class TestListEvents:
    """Tests for GET /api/events"""

    def test_list_events_empty(self, client, auth_headers):
        response = client.get("/api/events", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["events"] == []
        assert data["total"] == 0

    def test_list_events_with_data(self, client, auth_headers):
        # Create an event first
        client.post(
            "/api/events",
            json={"source": "test", "event_type": "test_event"},
            headers=auth_headers,
        )
        response = client.get("/api/events", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["events"]) == 1

    def test_list_events_pagination(self, client, auth_headers):
        # Create 3 events
        for i in range(3):
            client.post(
                "/api/events",
                json={"source": f"test-{i}", "event_type": "test_event"},
                headers=auth_headers,
            )
        response = client.get(
            "/api/events?page=1&page_size=2", headers=auth_headers
        )
        data = response.json()
        assert data["total"] == 3
        assert len(data["events"]) == 2
        assert data["total_pages"] == 2

    def test_list_events_filter_severity(self, client, auth_headers):
        client.post(
            "/api/events",
            json={"source": "test", "event_type": "malware_detected"},
            headers=auth_headers,
        )
        client.post(
            "/api/events",
            json={"source": "test", "event_type": "successful_login"},
            headers=auth_headers,
        )
        response = client.get(
            "/api/events?severity=critical", headers=auth_headers
        )
        data = response.json()
        assert data["total"] == 1
        assert data["events"][0]["severity"] == "critical"


class TestGetEvent:
    """Tests for GET /api/events/{event_id}"""

    def test_get_event(self, client, auth_headers):
        create_resp = client.post(
            "/api/events",
            json={"source": "test", "event_type": "test_event"},
            headers=auth_headers,
        )
        event_id = create_resp.json()["event"]["id"]

        response = client.get(f"/api/events/{event_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == event_id

    def test_get_event_not_found(self, client, auth_headers):
        response = client.get(
            "/api/events/nonexistent-id", headers=auth_headers
        )
        assert response.status_code == 404
