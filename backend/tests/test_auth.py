"""
Tests for authentication endpoints.
"""

import pytest


class TestRegister:
    """Tests for POST /api/auth/register"""

    def test_register_success(self, client):
        response = client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@secureops.local",
                "password": "StrongPass123!",
                "role": "analyst",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "newuser"
        assert data["user"]["role"] == "analyst"
        assert "password" not in data["user"]
        assert "password_hash" not in data["user"]

    def test_register_duplicate_username(self, client, test_user):
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "different@secureops.local",
                "password": "StrongPass123!",
            },
        )
        assert response.status_code == 409

    def test_register_duplicate_email(self, client, test_user):
        response = client.post(
            "/api/auth/register",
            json={
                "username": "differentuser",
                "email": "test@secureops.local",
                "password": "StrongPass123!",
            },
        )
        assert response.status_code == 409

    def test_register_short_password(self, client):
        response = client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@secureops.local",
                "password": "short",
            },
        )
        assert response.status_code == 422

    def test_register_invalid_username(self, client):
        response = client.post(
            "/api/auth/register",
            json={
                "username": "invalid user!",
                "email": "newuser@secureops.local",
                "password": "StrongPass123!",
            },
        )
        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/auth/login"""

    def test_login_success(self, client, test_user):
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "TestPass123!"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == "testuser"

    def test_login_wrong_password(self, client, test_user):
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "WrongPass!"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/api/auth/login",
            json={"username": "nouser", "password": "SomePass123!"},
        )
        assert response.status_code == 401

    def test_protected_endpoint_without_token(self, client):
        response = client.get("/api/events")
        assert response.status_code == 401

    def test_protected_endpoint_with_invalid_token(self, client):
        response = client.get(
            "/api/events",
            headers={"Authorization": "Bearer invalid-token-here"},
        )
        assert response.status_code == 401
