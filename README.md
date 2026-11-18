# 🛡️ SecureOps

<<<<<<< HEAD
**Cybersecurity Monitoring & Threat Detection Platform**

SecureOps is a full-stack security monitoring platform that collects security events, analyzes them using a rule-based detection engine, assigns severity levels, generates alerts, and presents the results through a professional web dashboard.

Built as a portfolio-grade project demonstrating practical skills in cybersecurity, Python, FastAPI, React, and secure software development.

---

## 🎯 Features

- **Security Dashboard** — Real-time overview with event timeline, severity distribution, and top threat sources
- **Event Management** — Submit, search, filter, and view security events with full detail
- **Threat Detection Engine** — 5 modular detection rules that automatically analyze events and generate alerts
- **Alert Management** — Track alerts through open → investigating → resolved workflow
- **JWT Authentication** — Secure login with role-based access (analyst/admin)
- **System Health** — Monitor API status, database connectivity, and uptime
- **Dark SOC Interface** — Professional cybersecurity-themed UI with glassmorphism design
- **Docker Ready** — Single command deployment with Docker Compose

---

## 🏗️ Architecture

```mermaid
flowchart TB
    subgraph Frontend["Frontend (React + Vite)"]
        UI[Dashboard / Events / Alerts / Health]
    end
    
    subgraph Backend["Backend (FastAPI)"]
        API[API Layer - Routers]
        SVC[Service Layer]
        DET[Detection Engine]
        DB_LAYER[Database Layer - SQLAlchemy]
    end
    
    subgraph Database["Database"]
        DB[(SQLite / PostgreSQL)]
    end
    
    UI -->|Axios + JWT| API
    API -->|Dependency Injection| SVC
    SVC --> DET
    SVC --> DB_LAYER
    DET --> DB_LAYER
    DB_LAYER --> DB
=======
### Cybersecurity Monitoring & Threat Detection Platform

SecureOps is a defensive cybersecurity platform designed to collect, analyze, and monitor security events through a centralized system.

The project combines **cybersecurity concepts with modern software development** to demonstrate how security events can be collected through APIs, stored, analyzed using detection rules, and eventually displayed through a security monitoring dashboard.

> 🚧 **Project Status:** Under Active Development

---

## 🎯 Project Objective

Modern systems generate large amounts of security-related events such as:

* Failed login attempts
* Successful authentications
* Suspicious network activity
* Privilege changes
* Malware detection events
* Unusual system behavior

Manually analyzing these events can be difficult.

SecureOps aims to provide a centralized platform that can:

```text
Security Events
       ↓
     REST API
       ↓
    Event Storage
       ↓
 Detection Engine
       ↓
 Threat Analysis
       ↓
    Security Alerts
       ↓
 Monitoring Dashboard
```

The goal is to build a small-scale **Security Operations Center (SOC) monitoring platform** for learning, demonstration, and portfolio purposes.

---

## 🚀 Planned Features

### 🔐 Authentication

* User registration
* Secure password hashing
* JWT-based authentication
* Role-based access
* Protected API endpoints

### 📥 Security Event Management

* Receive security events through REST APIs
* Validate incoming event data
* Store security events
* Search and filter events
* View individual event details

### 🧠 Threat Detection

A rule-based detection engine will analyze incoming events.

Planned detection rules include:

* Multiple failed login detection
* Suspicious authentication activity
* Suspicious port activity
* Privilege escalation indicators
* Safe sample malware indicators

Each detected event can receive a severity level:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

### 🚨 Alert Management

When suspicious activity is detected, SecureOps will generate security alerts.

Example:

```text
🚨 HIGH ALERT

Rule: Multiple Failed Logins
Source IP: 192.168.1.50
Event Type: failed_login
Status: OPEN
```

Alerts will support statuses such as:

```text
OPEN
INVESTIGATING
RESOLVED
```

### 📊 Security Dashboard

The planned dashboard will provide:

* Total security events
* Total alerts
* Critical alerts
* High-severity alerts
* Event timeline
* Severity distribution
* Recent alerts
* Top source IPs
* Event statistics

---

# 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │   Security Events   │
                    │                     │
                    │ Login / Network /   │
                    │ System / Security   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     REST API        │
                    │      FastAPI        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Event Processing  │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
             ┌─────────────┐      ┌───────────────┐
             │  Database   │      │   Detection   │
             │ SQLite /    │      │    Engine     │
             │ PostgreSQL  │      └───────┬───────┘
             └─────────────┘              │
                                         ▼
                                ┌─────────────────┐
                                │ Security Alerts │
                                └────────┬────────┘
                                         │
                                         ▼
                                ┌─────────────────┐
                                │ Security        │
                                │ Dashboard       │
                                └─────────────────┘
>>>>>>> 77c140dd3bb7225102d2f93c68ec4116763abe7a
```

---

<<<<<<< HEAD
## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11+, FastAPI, Uvicorn, SQLAlchemy, Pydantic |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS 3, Recharts |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Auth** | JWT (python-jose), bcrypt (passlib) |
| **Testing** | pytest, FastAPI TestClient |
| **DevOps** | Docker, Docker Compose |

---

## 📁 Project Structure

```
secureops/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routers
│   │   ├── core/           # Config, security, logging
│   │   ├── db/             # Database models & session
│   │   ├── detection/      # Detection rules & severity
│   │   ├── schemas/        # Pydantic request/response models
│   │   ├── services/       # Business logic layer
│   │   ├── main.py         # FastAPI application
│   │   └── seed.py         # Demo data seeder
│   ├── tests/              # pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── hooks/          # Auth context & hooks
│   │   ├── pages/          # Page components
│   │   ├── services/       # API client
│   │   └── types/          # TypeScript definitions
│   ├── package.json
│   └── Dockerfile
├── docs/                   # Architecture, API, detection rules docs
├── sample_data/            # Sample security events JSON
├── docker-compose.yml
├── .env.example
=======
# 🛠️ Technology Stack

## Backend

* Python
* FastAPI
* Uvicorn
* Pydantic
* SQLAlchemy

## Database

* SQLite for development
* PostgreSQL-ready architecture

## Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* Recharts

## Security

* JWT Authentication
* Password Hashing
* Input Validation
* Role-Based Access Control

## Testing

* Pytest
* FastAPI TestClient

## DevOps

* Docker
* Docker Compose
* Git & GitHub

---

# 📁 Project Structure

The project is being developed using a modular architecture:

```text
secureops/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── db/
│   │   ├── schemas/
│   │   ├── api/
│   │   ├── services/
│   │   └── detection/
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│
├── tests/
│
├── docs/
│
├── sample_data/
│
├── .env.example
├── .gitignore
├── docker-compose.yml
>>>>>>> 77c140dd3bb7225102d2f93c68ec4116763abe7a
└── README.md
```

---

<<<<<<< HEAD
## 🔍 Detection Engine

The detection engine evaluates 5 rules against every incoming security event:

| Rule | Severity | Trigger |
|------|----------|---------|
| Multiple Failed Logins | HIGH | ≥3 failed logins from same IP in 10 min |
| Suspicious Port Activity | MEDIUM | Connection attempts to restricted ports |
| Privilege Escalation | CRITICAL | Unauthorized admin actions or privilege changes |
| Suspicious Authentication | HIGH | Impossible travel, credential stuffing |
| Malware Indicator | CRITICAL | Known test malware signatures detected |

See [docs/detection-rules.md](docs/detection-rules.md) for detailed documentation.

---

## 🔗 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | No | API status |
| GET | `/health` | No | System health check |
| POST | `/api/auth/register` | No | Register user |
| POST | `/api/auth/login` | No | Login, get JWT |
| GET | `/api/events` | Yes | List events (search/filter/paginate) |
| POST | `/api/events` | Yes | Submit event → detect → alert |
| GET | `/api/events/{id}` | Yes | Event details + alerts |
| GET | `/api/alerts` | Yes | List alerts |
| GET | `/api/alerts/{id}` | Yes | Alert details |
| PATCH | `/api/alerts/{id}` | Yes | Update alert status |
| GET | `/api/dashboard/stats` | Yes | Dashboard statistics |
| GET | `/api/dashboard/timeline` | Yes | Timeline & chart data |
| GET | `/docs` | No | Swagger API docs |

See [docs/api.md](docs/api.md) for request/response examples.

---

## 🚀 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/secureops.git
cd secureops
```

### 2. Set up environment
```bash
cp .env.example .env
# Edit .env with your SECRET_KEY (generate a random one for production)
```

### 3. Backend setup
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Frontend setup
```bash
cd frontend
npm install
=======
# 🔌 API

SecureOps uses REST APIs for communication between the different components of the platform.

Planned core endpoints include:

| Method | Endpoint               | Purpose               |
| ------ | ---------------------- | --------------------- |
| GET    | `/`                    | API information       |
| GET    | `/health`              | Health check          |
| POST   | `/api/auth/register`   | Register user         |
| POST   | `/api/auth/login`      | User login            |
| GET    | `/api/events`          | Retrieve events       |
| POST   | `/api/events`          | Submit security event |
| GET    | `/api/events/{id}`     | Retrieve event        |
| GET    | `/api/alerts`          | Retrieve alerts       |
| GET    | `/api/alerts/{id}`     | Retrieve alert        |
| PATCH  | `/api/alerts/{id}`     | Update alert          |
| GET    | `/api/dashboard/stats` | Dashboard statistics  |

Interactive API documentation will be available through FastAPI Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

# 📦 Example Security Event

SecureOps can receive structured security information using JSON.

Example:

```json
{
  "event_type": "failed_login",
  "source_ip": "192.168.1.50",
  "description": "Failed login attempt"
}
```

The event can then be processed by the detection engine.

```text
JSON Event
    ↓
API
    ↓
Validation
    ↓
Database
    ↓
Detection Rules
    ↓
Alert
```

---

# 🧠 Detection Engine

The detection engine is one of the main cybersecurity components of SecureOps.

Example:

```text
Failed Login
      ↓
Same IP
      ↓
Multiple attempts
      ↓
Detection Rule
      ↓
Suspicious Activity
      ↓
HIGH Alert
```

The detection system is designed to be modular so additional security rules can be added in the future.

---

# 🧪 Testing

Automated tests will cover important application functionality, including:

* API health
* Authentication
* Event creation
* Event retrieval
* Detection rules
* Alert generation
* Dashboard statistics

Run tests with:

```bash
pytest
```

---

# ▶️ Running Locally

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd secureops
```

## 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate:

```powershell
.\venv\Scripts\Activate.ps1
```

## 3. Install backend dependencies

```powershell
cd backend
pip install -r requirements.txt
```

## 4. Start the backend

From the project root:

```powershell
uvicorn backend.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
>>>>>>> 77c140dd3bb7225102d2f93c68ec4116763abe7a
```

---

<<<<<<< HEAD
## 💻 Local Development

### Start Backend
```bash
cd backend
.\venv\Scripts\activate     # Windows
uvicorn app.main:app --reload
```
Backend runs at: http://localhost:8000  
API docs at: http://localhost:8000/docs

### Start Frontend
```bash
cd frontend
npm run dev
```
Frontend runs at: http://localhost:5173

### Demo Credentials
| Role | Username | Password |
|------|----------|----------|
| Analyst | `analyst` | `SecureOps2024!` |
| Admin | `admin` | `SecureOpsAdmin2024!` |

---

## 🐳 Docker Setup

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🧪 Testing

```bash
cd backend
.\venv\Scripts\activate
python -m pytest tests/ -v
```

Tests cover:
- Authentication (register, login, token validation)
- Event CRUD and auto-severity classification
- Detection engine rule triggers
- Dashboard statistics
- Health endpoint
- Protected endpoint access

---

## 📡 Example Security Events

Submit via API or use the pre-seeded demo data:

```bash
curl -X POST http://localhost:8000/api/events \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "auth-server",
    "source_ip": "192.168.1.50",
    "destination_ip": "192.168.1.10",
    "event_type": "failed_login",
    "description": "Multiple failed authentication attempts detected",
    "raw_data": {"username": "jdoe", "attempts": 5}
  }'
```

---

## 🔒 Security Considerations

- Passwords hashed with bcrypt (never stored as plaintext)
- JWT authentication with configurable expiration
- Input validation on all API endpoints (Pydantic schemas)
- Parameterized database queries via SQLAlchemy ORM
- Environment-based secrets (never hardcoded)
- CORS restricted to configured origins
- No sensitive data in error responses or logs
- Role-based access control

---

## 🔮 Future Improvements

- [ ] Real-time WebSocket event streaming
- [ ] Email/Slack alert notifications
- [ ] SIEM integration (Splunk, ELK)
- [ ] Machine learning anomaly detection
- [ ] Rate limiting and API throttling
- [ ] Audit logging
- [ ] Multi-tenancy support
- [ ] PostgreSQL migration with Alembic
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Event correlation engine

---

## 👤 Author

Built as a cybersecurity and software development portfolio project.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
=======
# 🔐 Security Considerations

SecureOps is designed as a defensive security project.

The project focuses on:

* Security monitoring
* Event analysis
* Threat detection
* Alert management
* Secure authentication
* Secure software development

The project does **not** implement:

* Malware
* Credential theft
* Destructive attacks
* Unauthorized exploitation
* Persistence mechanisms

All security events used for demonstrations can be simulated using fictional/private test data.

---

# 🔮 Future Improvements

Planned improvements include:

* Real-time event streaming
* WebSocket-based live alerts
* Linux authentication log integration
* Windows event log integration
* IP reputation integration
* More advanced detection rules
* Machine-learning-assisted anomaly detection
* PostgreSQL deployment
* Redis-based event processing
* Dockerized production deployment
* Cloud deployment
* Email/security alert notifications
* SIEM-style search
* Advanced analyst workflows

---

# 📚 Learning Objectives

This project is being developed to gain practical experience in:

* Cybersecurity monitoring
* SOC concepts
* Threat detection
* Security event analysis
* REST API development
* Backend engineering
* Database management
* Authentication
* Frontend development
* Automated testing
* Containerization
* Git/GitHub workflow
* Secure software development

---

# 👨‍💻 Author

**Amal Krishna A.K**

B.Tech Computer Science & Engineering — Cyber Security

Interested in:

* Cybersecurity
* Software Development
* Network Security
* Security Engineering
* Threat Detection

---

## ⭐ Project Status

**🚧 SecureOps is currently under active development.**

The project is being built incrementally, starting with the backend API and gradually adding event processing, threat detection, alert management, authentication, dashboard functionality, testing, and deployment.

---

## 📜 License

This project is intended for educational, portfolio, and defensive cybersecurity purposes.
>>>>>>> 77c140dd3bb7225102d2f93c68ec4116763abe7a
