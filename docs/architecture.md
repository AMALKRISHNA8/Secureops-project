# SecureOps Architecture

## Overview

SecureOps follows a clean, layered architecture that separates concerns across the frontend, API, services, detection engine, and database.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                     Frontend (React)                      │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌───────────────┐ │
│  │Dashboard │ │ Events   │ │ Alerts │ │ System Health │ │
│  └────┬─────┘ └────┬─────┘ └───┬────┘ └──────┬────────┘ │
│       │             │           │              │          │
│       └─────────────┴───────────┴──────────────┘          │
│                         │ Axios HTTP                      │
└─────────────────────────┼────────────────────────────────┘
                          │
┌─────────────────────────┼────────────────────────────────┐
│               FastAPI Backend                             │
│                         │                                 │
│  ┌──────────────────────┴──────────────────────────────┐ │
│  │                 API Layer (Routers)                   │ │
│  │  /api/auth  /api/events  /api/alerts  /api/dashboard │ │
│  └──────────────────────┬──────────────────────────────┘ │
│                         │                                 │
│  ┌──────────────────────┴──────────────────────────────┐ │
│  │              Service Layer                           │ │
│  │  EventService  AlertService  DetectionEngine         │ │
│  └──────────────────────┬──────────────────────────────┘ │
│                         │                                 │
│  ┌──────────────────────┴──────────────────────────────┐ │
│  │            Detection Engine                          │ │
│  │  Rules → Severity Classification → Alert Generation  │ │
│  └──────────────────────┬──────────────────────────────┘ │
│                         │                                 │
│  ┌──────────────────────┴──────────────────────────────┐ │
│  │         Database Layer (SQLAlchemy ORM)               │ │
│  │  User  SecurityEvent  Alert                          │ │
│  └──────────────────────┬──────────────────────────────┘ │
│                         │                                 │
└─────────────────────────┼────────────────────────────────┘
                          │
                ┌─────────┴─────────┐
                │   SQLite / PostgreSQL  │
                └───────────────────┘
```

## Component Details

### Frontend (React + TypeScript + Vite)
- **Pages**: Dashboard, Events, Event Detail, Alerts, Health, Login
- **State**: React Context for auth, component-level state for data
- **API Client**: Axios with JWT interceptor
- **Charts**: Recharts (Area, Pie, Bar charts)
- **Styling**: Tailwind CSS v3 with dark cybersecurity theme

### API Layer (FastAPI Routers)
- Handles HTTP requests, input validation (Pydantic), and responses
- JWT authentication via OAuth2 bearer tokens
- CORS middleware for frontend communication

### Service Layer
- **EventService**: CRUD operations, search/filter/pagination
- **AlertService**: CRUD, status management (open → investigating → resolved)
- **DetectionEngine**: Orchestrates rule execution, creates alerts

### Detection Engine
- 5 modular detection rules (failed logins, port activity, privilege escalation, suspicious auth, malware indicators)
- Each rule receives an event and returns a match result
- Severity auto-classification based on event type

### Database Layer
- SQLAlchemy ORM with declarative models
- SQLite for development, PostgreSQL-ready via `DATABASE_URL`
- UUID primary keys for all models
- Proper relationships (SecurityEvent ↔ Alert)

## Security Architecture
- Passwords hashed with bcrypt (passlib)
- JWT tokens with configurable expiration
- Protected endpoints via `get_current_user` dependency
- Environment-based secrets (never hardcoded)
- CORS restricted to configured origins
- Input validation on all endpoints (Pydantic)
- No sensitive data in API error responses
