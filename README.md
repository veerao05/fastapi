# Order Management System - Async FastAPI

A production-ready Order Management System built with FastAPI, demonstrating best practices in async Python development with JWT authentication, layered architecture, structured logging, and Docker deployment.

## Features

- **JWT Authentication** - Register, login, and secure endpoints with Bearer tokens
- **User-scoped Orders** - Each user can only see and manage their own orders
- **Full CRUD Operations** - Create, Read, Update, Delete orders
- **Async/Await** - High-performance asynchronous operations throughout
- **PostgreSQL + asyncpg** - Production database with async driver
- **Layered Architecture** - API → Service → Database pattern
- **Custom Exception Handling** - Typed exceptions with structured JSON error responses
- **Data Validation** - Pydantic v2 schemas with strict validation rules
- **Structured Logging** - Rotating file logs + console output via `logging.ini`
- **Logging Middleware** - Logs every request and response automatically
- **Alembic Migrations** - Schema versioning and safe database migrations
- **Docker Support** - Dockerfile + docker-compose for easy deployment
- **Test Suite** - Async pytest tests with in-memory SQLite (no real DB needed)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                  │
├─────────────────────────────────────────────────────────┤
│  Middleware (LoggingMiddleware)                          │
│  - Logs every incoming request and response status      │
├─────────────────────────────────────────────────────────┤
│  API Layer  (api/order_api.py + api/v1/endpoints/)      │
│  - HTTP request/response handling                       │
│  - Route definitions & dependency injection             │
│  - JWT verification via HTTPBearer                      │
├─────────────────────────────────────────────────────────┤
│  Service Layer (services/order_service.py)              │
│  - Business logic, duplicate-order checks               │
│  - Raises typed exceptions (OrderNotFoundException …)   │
├─────────────────────────────────────────────────────────┤
│  Models & Schemas (models/ & schemas/)                  │
│  - SQLAlchemy models & Pydantic schemas                 │
├─────────────────────────────────────────────────────────┤
│  Database Layer (PostgreSQL + SQLAlchemy async)         │
│  - Async connection handling & data persistence         │
└─────────────────────────────────────────────────────────┘
```

## Project Structure

```
fastapi/
├── Dockerfile                          # Docker image definition
├── docker-compose.yml                  # Docker Compose for deployment
├── .dockerignore                       # Files excluded from Docker build
├── .env                                # Environment variables (not committed)
├── pytest.ini                          # Pytest configuration
├── requirements.txt                    # Python dependencies
├── alembic.ini                         # Alembic configuration
├── alembic/
│   ├── env.py                          # Alembic async environment setup
│   └── versions/                       # Migration scripts (auto-generated)
├── config/
│   └── logging.ini                     # Logging configuration
├── var/
│   └── logs/                           # Log files (auto-created at startup)
│       ├── cog.log                     # INFO+ logs (rotating, 5MB × 5)
│       └── cog-error.log               # ERROR+ logs (rotating, 5MB × 5)
├── tests/
│   ├── conftest.py                     # Shared fixtures (in-memory SQLite, auth client)
│   ├── test_health.py                  # Tests for / and /health
│   ├── test_auth.py                    # Register + login tests
│   └── test_order_api.py               # Full order CRUD + data isolation tests
└── app/
    ├── main.py                         # Application entry point
    ├── api/
    │   ├── order_api.py                # Order routes (/api/orders/)
    │   └── v1/
    │       ├── router.py               # v1 API router
    │       └── endpoints/
    │           ├── auth.py             # Register + Login endpoints
    │           └── users.py            # User profile endpoint
    ├── core/
    │   ├── deps.py                     # JWT dependency (get_current_user)
    │   ├── security.py                 # bcrypt password hashing
    │   └── settings.py                 # App settings from .env
    ├── db/
    │   └── database.py                 # Async database setup
    ├── middleware/
    │   └── logging_middleware.py       # Request/response logging middleware
    ├── models/
    │   ├── user.py                     # SQLAlchemy User model
    │   └── order.py                    # SQLAlchemy Order model
    ├── schemas/
    │   ├── user.py                     # Pydantic user schemas
    │   └── order_schema.py             # Pydantic order schemas
    ├── services/
    │   └── order_service.py            # Order business logic
    └── utils/
        ├── constants.py                # App-wide constants (LOGS_DIR, etc.)
        └── exceptions.py              # Custom exceptions & handlers
```

## Prerequisites

- Python 3.12+
- PostgreSQL (for local development)
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

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/orders
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Create the database

```bash
psql -U postgres -c "CREATE DATABASE orders;"
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the application

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

## Authentication Flow

This API uses **JWT Bearer token** authentication. All order endpoints require a valid token.

### Step 1 — Register a user

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "Secret@123"}'
```

### Step 2 — Login to get a token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=Secret@123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Step 3 — Use the token

Pass the token in the `Authorization` header for all order requests:

```bash
-H "Authorization: Bearer <access_token>"
```

> **Swagger UI**: Click the **Authorize 🔒** button at the top right, paste the token, and all order endpoints are unlocked.

---

## API Endpoints

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | No | Register a new user |
| POST | `/api/v1/auth/login` | No | Login and receive JWT token |

### Orders

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/orders/` | Yes | Create a new order |
| GET | `/api/orders/` | Yes | List all your orders |
| GET | `/api/orders/{id}` | Yes | Get order by ID |
| PUT | `/api/orders/{id}` | Yes | Update an order |
| DELETE | `/api/orders/{id}` | Yes | Delete an order |

### System

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | No | Welcome message |
| GET | `/health` | No | Health check |

---

## curl Examples (Orders)

Replace `<token>` with the `access_token` from the login response.

### Create order
```bash
curl -X POST "http://localhost:8000/api/orders/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Wireless Mouse", "quantity": 2, "unit_price": 29.99}'
```

### List orders
```bash
curl "http://localhost:8000/api/orders/" \
  -H "Authorization: Bearer <token>"
```

### Get order by ID
```bash
curl "http://localhost:8000/api/orders/1" \
  -H "Authorization: Bearer <token>"
```

### Update order
```bash
curl -X PUT "http://localhost:8000/api/orders/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```

### Delete order
```bash
curl -X DELETE "http://localhost:8000/api/orders/1" \
  -H "Authorization: Bearer <token>"
```

---

## Running Tests

Tests use an **in-memory SQLite database** — no PostgreSQL or `.env` needed.

```bash
pytest
```

To run a specific file:

```bash
pytest tests/test_auth.py
pytest tests/test_order_api.py
pytest tests/test_health.py
```

To run with verbose output:

```bash
pytest -v
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

## Technology Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Web framework |
| **SQLAlchemy 2.0** | Async ORM |
| **PostgreSQL + asyncpg** | Production database |
| **aiosqlite** | In-memory database for tests |
| **Pydantic v2** | Data validation & serialisation |
| **python-jose** | JWT token creation and verification |
| **bcrypt** | Password hashing |
| **Alembic** | Database schema migrations |
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

### Database connection error
Ensure PostgreSQL is running and your `.env` `DATABASE_URL` is correct:
```bash
psql -U postgres -c "\l"   # list databases
psql -U postgres -c "CREATE DATABASE orders;"
```

### Run a specific migration
```bash
alembic upgrade head          # apply all pending migrations
alembic downgrade -1          # roll back the last migration
alembic history               # view migration history
```