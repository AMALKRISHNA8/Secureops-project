"""
SecureOps — Cybersecurity Monitoring & Threat Detection Platform

Main FastAPI application entry point.
"""

import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.database import create_tables

# Setup logging
setup_logging()
logger = logging.getLogger("secureops")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("Starting SecureOps v%s", settings.APP_VERSION)

    # Create database tables
    create_tables()
    logger.info("Database tables created/verified")

    # Seed demo data on first run
    from app.seed import seed_demo_data
    seed_demo_data()

    yield

    logger.info("SecureOps shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description="Cybersecurity Monitoring & Threat Detection Platform",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Mount API Routers ---
from app.api.auth import router as auth_router
from app.api.events import router as events_router
from app.api.alerts import router as alerts_router
from app.api.dashboard import router as dashboard_router
from app.api.health import router as health_router

app.include_router(auth_router)
app.include_router(events_router)
app.include_router(alerts_router)
app.include_router(dashboard_router)
app.include_router(health_router)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint — confirms the API is running."""
    return {
        "message": "SecureOps API is running",
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": "/docs",
    }
