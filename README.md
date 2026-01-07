# Employee Management System - Async FastAPI

A professional, production-ready Employee Management System built with FastAPI, demonstrating best practices in async Python development with proper layered architecture.

## 🎯 Features

- ✅ **Full CRUD Operations** - Create, Read, Update, Delete employees
- ✅ **Async/Await** - High-performance asynchronous operations
- ✅ **SQLite Integration** - Lightweight database with async support
- ✅ **Layered Architecture** - Controller → Service → Repository pattern
- ✅ **Business Logic** - Salary validation, department normalization, increase limits
- ✅ **Custom Exception Handling** - Detailed, user-friendly error responses
- ✅ **Search & Filter** - Find employees by name or department
- ✅ **Statistics** - Comprehensive organizational analytics
- ✅ **Pagination** - Efficient data retrieval for large datasets
- ✅ **Data Validation** - Pydantic schemas with strict validation rules

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                  │
├─────────────────────────────────────────────────────────┤
│  API Layer (api/employee_api.py)                        │
│  - HTTP request/response handling                       │
│  - Route definitions                                    │
│  - Dependency injection                                 │
├─────────────────────────────────────────────────────────┤
│  Service Layer (services/employee_service.py)           │
│  - Business logic                                       │
│  - Validation rules                                     │
│  - Data transformation                                  │
├─────────────────────────────────────────────────────────┤
│  Models & Schemas (models/ & schemas/)                   │
│  - Database models (SQLAlchemy)                         │
│  - Data validation schemas (Pydantic)                   │
│  - Request/Response models                              │
├─────────────────────────────────────────────────────────┤
│  Database Layer (SQLite + SQLAlchemy)                   │
│  - Data persistence                                     │
│  - Async connection handling                            │
└─────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- Python 3.10 or higher
- SQLite3 (included with Python)
- pip (Python package manager)

## 🚀 Installation & Setup

### 1. Clone or Extract the Project

```bash
cd fastapi
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup (SQLite)

The application uses SQLite database which is created automatically when you run the application. No additional database setup is required as SQLite is file-based and will be created in the project root as `employees.db`.

### 5. Run the Application

```bash
# From the project root directory
python -m app.main

# Or alternatively:
cd app
python main.py
```

The application will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 6. Verify Database Creation

After running the application for the first time, verify the database was created:

```bash
# Check if database file exists
ls -la employees.db

# Access SQLite database
sqlite3 employees.db

# In SQLite prompt, check tables
.tables

# View table structure
.schema employees

# View all employees
SELECT * FROM employees;

# Exit SQLite
.quit
```

## 📚 API Endpoints

### Employee Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/employees/` | Create a new employee |
| GET | `/api/employees/` | Get all employees (with pagination) |
| GET | `/api/employees/{id}` | Get employee by ID |
| PUT | `/api/employees/{id}` | Update employee |
| DELETE | `/api/employees/{id}` | Delete employee |

### Search & Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/employees/search/filter` | Search by name or department |
| GET | `/api/employees/statistics/summary` | Get employee statistics |
| GET | `/api/employees/departments/list` | Get all departments |

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check |
| GET | `/info` | Application info |

## 🎬 Video Demonstration Steps

### Step 1: Basic Welcome Route
```bash
# Run the application
python main.py

# Visit http://localhost:8000
# Visit http://localhost:8000/docs
```

### Step 2: Create First Employee (POST)

Using Swagger UI at `/docs`:

```json
{
  "name": "John Doe",
  "email": "john.doe@company.com",
  "department": "engineering",
  "salary": 75000
}
```

Verify in SQLite:
```bash
sqlite3 employees.db
SELECT * FROM employees;
.quit
```

### Step 3: Get All Employees (GET)

```bash
# Get all employees
GET /api/employees/

# With pagination
GET /api/employees/?skip=0&limit=10
```

### Step 4: Get Single Employee (GET by ID)

```bash
GET /api/employees/1
```

### Step 5: Update Employee (PUT)

```json
{
  "name": "John Updated",
  "salary": 85000
}
```

### Step 6: Delete Employee (DELETE)

```bash
DELETE /api/employees/1
```

### Step 7: Custom Exception Handling

Try these to see error responses:

1. **Create employee with existing email** → 400 Bad Request
2. **Get non-existent employee** → 404 Not Found
3. **Create with salary below $30,000** → 400 Invalid Salary
4. **Update with >20% salary increase** → 400 Invalid Salary
5. **Invalid email format** → 422 Validation Error

### Step 8: Advanced Features

**Search by name:**
```bash
GET /api/employees/search/filter?name=john
```

**Filter by department:**
```bash
GET /api/employees/search/filter?department=engineering
```

**Get statistics:**
```bash
GET /api/employees/statistics/summary
```

**Get all departments:**
```bash
GET /api/employees/departments/list
```

## 🧪 Testing with curl

### Create Employee
```bash
curl -X POST "http://localhost:8000/api/employees/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane.smith@company.com",
    "department": "Sales",
    "salary": 65000
  }'
```

### Get All Employees
```bash
curl "http://localhost:8000/api/employees/"
```

### Get Employee by ID
```bash
curl "http://localhost:8000/api/employees/1"
```

### Update Employee
```bash
curl -X PUT "http://localhost:8000/api/employees/1" \
  -H "Content-Type: application/json" \
  -d '{
    "salary": 70000
  }'
```

### Delete Employee
```bash
curl -X DELETE "http://localhost:8000/api/employees/1"
```

## 🎯 Business Rules

### Salary Rules
- Minimum salary: **$30,000**
- Maximum salary: **$500,000**
- Maximum salary increase per update: **20%**
- Increases above 20% require manager approval

### Email Rules
- Must be unique across all employees
- Must be valid email format
- Cannot be changed if already in use by another employee

### Department Rules
- Department names are automatically normalized to Title Case
- Examples: "engineering" → "Engineering", "SALES" → "Sales"

## 📁 Project Structure

```
FastApi/
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── employees.db                    # SQLite database (auto-created)
├── test_employee_endpoints.py      # API tests
└── app/                           # Main application package
    ├── __init__.py
    ├── main.py                    # Application entry point
    ├── api/                       # API layer
    │   ├── __init__.py
    │   └── employee_api.py        # Employee routes
    ├── db/                        # Database configuration
    │   ├── __init__.py
    │   └── database.py            # Async database setup
    ├── models/                    # Data models
    │   ├── __init__.py
    │   └── employee.py            # SQLAlchemy models
    ├── schemas/                   # Data validation
    │   ├── __init__.py
    │   └── model_schema.py        # Pydantic schemas
    ├── services/                  # Business logic layer
    │   ├── __init__.py
    │   └── employee_service.py    # Employee business logic
    ├── utils/                     # Utilities
    │   ├── __init__.py
    │   └── exceptions.py          # Custom exceptions
    └── middleware/                # Middleware components
        └── __init__.py
```

## 🔧 Technology Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy 2.0** - SQL toolkit and ORM with async support
- **SQLite** - Lightweight, file-based relational database
- **aiosqlite** - Async SQLite database client library
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - Lightning-fast ASGI server
- **python-dotenv** - Environment variable management

## 🎓 Learning Objectives

This project demonstrates:

1. **Async/Await** - Proper use of async operations in FastAPI
2. **Layered Architecture** - Separation of concerns (Controller/Service/Repository)
3. **Dependency Injection** - Using FastAPI's dependency system
4. **Exception Handling** - Custom exceptions and error responses
5. **Business Logic** - Implementing validation rules and constraints
6. **Database Operations** - Async SQLAlchemy with SQLite
7. **API Design** - RESTful endpoints with proper HTTP methods
8. **Documentation** - Auto-generated API docs with Swagger UI

## 🐛 Troubleshooting

### Database File Not Found
```bash
# Solution: Make sure you're in the correct directory and run the app first
cd /path/to/fastapi
python -m app.main
# Database will be created automatically
```

### Import Errors
```bash
# Solution: Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Solution: Kill the process using port 8000
lsof -ti:8000 | xargs kill -9
# Or change port in main.py
```

### Database Inspection Commands
```bash
# Check if database exists
ls -la employees.db

# Open SQLite database
sqlite3 employees.db

# Common SQLite commands:
.tables                    # List all tables
.schema employees         # Show table structure
SELECT * FROM employees;  # View all records
.quit                     # Exit SQLite
```

## 📝 License

MIT License - feel free to use this project for learning and development!

## 👨‍💻 Author

Created by **Veena** for educational purposes demonstrating professional FastAPI development with async operations.

---

**Happy Coding! 🚀**
