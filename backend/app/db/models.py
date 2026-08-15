"""
SQLAlchemy ORM models for SecureOps.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


# --- Enums ---

class UserRole(str, enum.Enum):
    ANALYST = "analyst"
    ADMIN = "admin"


class SeverityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventStatus(str, enum.Enum):
    NEW = "new"
    REVIEWED = "reviewed"
    ESCALATED = "escalated"
    CLOSED = "closed"


class AlertStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"


# --- Helper ---

def generate_uuid() -> str:
    return str(uuid.uuid4())


# --- Models ---

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.ANALYST, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User(username='{self.username}', role='{self.role}')>"


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    source = Column(String(100), nullable=False)
    source_ip = Column(String(45), nullable=True, index=True)
    destination_ip = Column(String(45), nullable=True)
    event_type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    severity = Column(SAEnum(SeverityLevel), default=SeverityLevel.LOW, nullable=False, index=True)
    status = Column(SAEnum(EventStatus), default=EventStatus.NEW, nullable=False)
    raw_data = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship to alerts
    alerts = relationship("Alert", back_populates="event", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<SecurityEvent(type='{self.event_type}', severity='{self.severity}')>"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_id = Column(
        String(36), ForeignKey("security_events.id"), nullable=False, index=True
    )
    rule_name = Column(String(100), nullable=False)
    severity = Column(SAEnum(SeverityLevel), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SAEnum(AlertStatus), default=AlertStatus.OPEN, nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship to event
    event = relationship("SecurityEvent", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<Alert(rule='{self.rule_name}', severity='{self.severity}')>"
