# SecureOps API Documentation

Base URL: `http://localhost:8000`

## Authentication

All endpoints except `/`, `/health`, and `/docs` require a JWT bearer token.

Include the token in the `Authorization` header:
```
Authorization: Bearer <your_token>
```

---

## Endpoints

### Root

#### `GET /`
Returns API status.

**Response:**
```json
{
  "message": "SecureOps API is running",
  "version": "1.0.0",
  "status": "online",
  "docs": "/docs"
}
```

---

### Health

#### `GET /health`
System health check (no auth required).

**Response:**
```json
{
  "status": "healthy",
  "api": "online",
  "database": "healthy",
  "version": "1.0.0",
  "uptime": "2h 15m 30s",
  "uptime_seconds": 8130,
  "timestamp": "2024-01-15T10:30:00+00:00"
}
```

---

### Authentication

#### `POST /api/auth/register`
Register a new user.

**Request:**
```json
{
  "username": "analyst01",
  "email": "analyst01@secureops.local",
  "password": "StrongPass123!",
  "role": "analyst"
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJI...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "analyst01",
    "email": "analyst01@secureops.local",
    "role": "analyst",
    "created_at": "2024-01-15T10:00:00+00:00"
  }
}
```

#### `POST /api/auth/login`
Authenticate and receive a JWT.

**Request:**
```json
{
  "username": "analyst",
  "password": "SecureOps2024!"
}
```

**Response (200):** Same structure as register.

---

### Security Events

#### `GET /api/events`
List events with search, filter, and pagination.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| page | int | Page number (default: 1) |
| page_size | int | Items per page (1-100, default: 20) |
| search | string | Search in description, source, IP, type |
| severity | string | Filter: low/medium/high/critical |
| event_type | string | Filter by event type |
| status | string | Filter: new/reviewed/escalated/closed |
| source_ip | string | Filter by source IP |

**Response (200):**
```json
{
  "events": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

#### `POST /api/events`
Submit a new security event. Automatically processed by the detection engine.

**Request:**
```json
{
  "source": "auth-server",
  "source_ip": "192.168.1.50",
  "destination_ip": "192.168.1.10",
  "event_type": "failed_login",
  "description": "Multiple failed authentication attempts detected",
  "raw_data": {"username": "jdoe", "attempts": 5}
}
```

**Response (201):**
```json
{
  "event": { ... },
  "alerts_generated": 1
}
```

#### `GET /api/events/{event_id}`
Get event details with associated alerts.

---

### Alerts

#### `GET /api/alerts`
List alerts with optional filtering.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| page | int | Page number |
| page_size | int | Items per page |
| severity | string | Filter by severity |
| status | string | Filter: open/investigating/resolved |

#### `GET /api/alerts/{alert_id}`
Get a specific alert.

#### `PATCH /api/alerts/{alert_id}`
Update alert status.

**Request:**
```json
{
  "status": "investigating"
}
```

---

### Dashboard

#### `GET /api/dashboard/stats`
Aggregate security statistics.

**Response (200):**
```json
{
  "total_events": 1250,
  "total_alerts": 47,
  "critical_alerts": 3,
  "high_alerts": 12,
  "medium_alerts": 21,
  "low_alerts": 11,
  "open_alerts": 25,
  "investigating_alerts": 10,
  "resolved_alerts": 12,
  "events_today": 42
}
```

#### `GET /api/dashboard/timeline`
Timeline and distribution data for charts.

**Response (200):**
```json
{
  "timeline": [{"date": "2024-01-01", "count": 15}, ...],
  "severity_distribution": [{"severity": "high", "count": 25}, ...],
  "top_source_ips": [{"source_ip": "192.168.1.50", "count": 12}, ...],
  "top_event_types": [{"event_type": "failed_login", "count": 30}, ...]
}
```

---

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict (duplicate resource) |
| 422 | Validation Error |
| 500 | Internal Server Error |
