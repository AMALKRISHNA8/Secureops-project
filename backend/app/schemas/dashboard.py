"""
Pydantic schemas for dashboard statistics endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel


class DashboardStats(BaseModel):
    """Aggregate security statistics for the dashboard."""
    total_events: int
    total_alerts: int
    critical_alerts: int
    high_alerts: int
    medium_alerts: int
    low_alerts: int
    open_alerts: int
    investigating_alerts: int
    resolved_alerts: int
    events_today: int


class TimelineEntry(BaseModel):
    """A single data point for the event timeline chart."""
    date: str
    count: int


class SeverityCount(BaseModel):
    """Event count grouped by severity level."""
    severity: str
    count: int


class TopSourceIP(BaseModel):
    """Source IP with event count."""
    source_ip: str
    count: int


class TopEventType(BaseModel):
    """Event type with count."""
    event_type: str
    count: int


class DashboardTimeline(BaseModel):
    """Full dashboard timeline and breakdown data."""
    timeline: List[TimelineEntry]
    severity_distribution: List[SeverityCount]
    top_source_ips: List[TopSourceIP]
    top_event_types: List[TopEventType]
