"""
Shared test fixtures for SecureOps backend tests.
Uses an in-memory SQLite database for isolation.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure the backend directory is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.database import Base, get_db
from app.db.models import User, UserRole
from app.core.security import hash_password
from app.main import app


# In-memory SQLite for test isolation
SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the get_db dependency with a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create all tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def test_db():
    """Direct database session for test setup."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(test_db):
    """Create and return a test analyst user."""
    user = User(
        username="testuser",
        email="test@secureops.local",
        password_hash=hash_password("TestPass123!"),
        role=UserRole.ANALYST,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def admin_user(test_db):
    """Create and return a test admin user."""
    user = User(
        username="testadmin",
        email="admin@secureops.local",
        password_hash=hash_password("AdminPass123!"),
        role=UserRole.ADMIN,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get auth headers for the test analyst user."""
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "TestPass123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client, admin_user):
    """Get auth headers for the test admin user."""
    response = client.post(
        "/api/auth/login",
        json={"username": "testadmin", "password": "AdminPass123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
