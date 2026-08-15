"""
SecureOps — Thin re-export for backwards compatibility.

Run with: uvicorn app.main:app --reload
From the backend/ directory.
"""

from app.main import app  # noqa: F401