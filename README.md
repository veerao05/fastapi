# Employee Management System - Async FastAPI

A production-ready Employee Management System built with FastAPI, demonstrating best practices in async Python development with proper layered architecture, structured logging, and Docker deployment.

## Features

- **Full CRUD Operations** - Create, Read, Update, Delete employees
- **Async/Await** - High-performance asynchronous operations
- **SQLite Integration** - Lightweight database with async support
- **Layered Architecture** - API → Service → Database pattern
- **Structured Logging** - Rotating file logs + console output via `logging.ini`
- **Logging Middleware** - Logs every request and response automatically
- **Custom Exception Handling** - Detailed, user-friendly error responses
- **Data Validation** - Pydantic schemas with strict validation rules
- **Docker Support** - Dockerfile + docker-compose for easy deployment
- **Test Suite** - Async pytest tests with in-memory SQLite

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                  │
├─────────────────────────────────────────────────────────┤
│  Middleware (LoggingMiddleware)                          │
│  - Logs every incoming request and response status      │
├─────────────────────────────────────────────────────────┤
│  API Layer (api/employee_api.py)                        │
│  - HTTP request/response handling                       │
│  - Route definitions & dependency injection             │
├─────────────────────────────────────────────────────────┤
│  Service Layer (services/employee_service.py)           │
│  - Business logic & validation rules                    │
├─────────────────────────────────────────────────────────┤
│  Models & Schemas (models/ & schemas/)                  │
│  - SQLAlchemy models & Pydantic schemas                 │
├─────────────────────────────────────────────────────────┤
│  Database Layer (SQLite + SQLAlchemy async)             │
│  - Async connection handling & data persistence         │
└─────────────────────────────────────────────────────────┘
```

## Project Structure

```
fastapi/
├── Dockerfile                      # Docker image definition
├── docker-compose.yml              # Docker Compose for deployment
├── .dockerignore                   # Files excluded from Docker build
├── pytest.ini                      # Pytest configuration
├── requirements.txt                # Python dependencies
├── config/
│   └── logging.ini                 # Logging configuration
├── var/
│   └── logs/                       # Log files (auto-created at startup)
│       ├── cog.log                 # INFO+ logs (rotating, 5MB x 5)
│       └── cog-error.log           # ERROR+ logs (rotating, 5MB x 5)
├── tests/
│   ├── conftest.py                 # Shared fixtures (in-memory DB, client)
│   ├── test_health.py              # Tests for / and /health
│   └── test_employee_api.py        # Full CRUD endpoint tests
└── app/
    ├── main.py                     # Application entry point
    ├── api/
    │   └── employee_api.py         # Employee routes
    ├── db/
    │   └── database.py             # Async database setup
    ├── middleware/
    │   ├── __init__.py
    │   └── logging_middleware.py   # Request/response logging middleware
    ├── models/
    │   └── employee.py             # SQLAlchemy model
    ├── schemas/
    │   └── model_schema.py         # Pydantic schemas
    ├── services/
    │   └── employee_service.py     # Employee business logic
    └── utils/
        ├── constants.py            # App-wide constants (LOGS_DIR, etc.)
        └── exceptions.py           # Custom exceptions & handlers
```

## Prerequisites

- Python 3.12+
- Docker & Docker Compose (for containerised deployment)

---

## Running Locally

### 1. Create & activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The app will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Logs are written to `var/logs/cog.log` (INFO+) and `var/logs/cog-error.log` (ERROR+), and also printed to the console.

---

## Running with Docker

### Build and start

```bash
docker-compose up --build
```

### Start in background

```bash
docker-compose up --build -d
```

### Stop

```bash
docker-compose down
```

The container:
- Exposes port **8000**
- Persists logs in a named Docker volume (`app_logs` → `/app/var/logs`)
- Health-checks `GET /health` every 30 seconds

---

## API Endpoints

### Employee Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/employees/` | Create a new employee |
| GET | `/api/employees/` | Get all employees |
| GET | `/api/employees/{id}` | Get employee by ID |
| PUT | `/api/employees/{id}` | Update employee |
| DELETE | `/api/employees/{id}` | Delete employee |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check |

---

## Running Tests

Tests use an **in-memory SQLite database** so they are fully isolated from the real DB.

```bash
pytest
```

To run a specific file:

```bash
pytest tests/test_employee_api.py
pytest tests/test_health.py
```

---

## Logging

Logging is configured via `config/logging.ini`. On startup the app automatically creates `var/logs/` if it doesn't exist.

| Handler | Level | Destination |
|---------|-------|-------------|
| `consoleHandler` | DEBUG | stdout |
| `debugHandler` | INFO | `var/logs/cog.log` (rotating 5 MB × 5) |
| `errorHandler` | ERROR | `var/logs/cog-error.log` (rotating 5 MB × 5) |

---

## curl Examples

### Create employee
```bash
curl -X POST "http://localhost:8000/api/employees/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Smith", "email": "jane.smith@example.com", "department": "Sales", "salary": 65000}'
```

### Get all employees
```bash
curl "http://localhost:8000/api/employees/"
```

### Get employee by ID
```bash
curl "http://localhost:8000/api/employees/1"
```

### Update employee
```bash
curl -X PUT "http://localhost:8000/api/employees/1" \
  -H "Content-Type: application/json" \
  -d '{"salary": 70000}'
```

### Delete employee
```bash
curl -X DELETE "http://localhost:8000/api/employees/1"
```

---

## Technology Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Web framework |
| **SQLAlchemy 2.0** | Async ORM |
| **SQLite + aiosqlite** | Database |
| **Pydantic v2** | Data validation |
| **Uvicorn** | ASGI server |
| **Docker + Compose** | Containerisation & deployment |
| **pytest + pytest-asyncio** | Async test suite |
| **httpx** | Async HTTP client for tests |

---

## Troubleshooting

### Port already in use
```bash
lsof -ti:8000 | xargs kill -9
```

### Docker container not starting
```bash
docker-compose logs app
```

### Inspect the SQLite database
```bash
sqlite3 employees.db
.tables
SELECT * FROM employees;
.quit
```