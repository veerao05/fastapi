import logging.config
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import app.models  # noqa: F401 — registers Order + User with Base.metadata
import app.utils.constants as const
from app.api.order_api import router as order_router
from app.api.v1.router import api_router
from app.db.database import create_tables_if_not_exist
from app.middleware import LoggingMiddleware
from app.utils.exceptions import (
    OrderNotFoundException,
    OrderAlreadyExistsException,
    order_not_found_exception_handler,
    order_already_exists_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from fastapi.exceptions import RequestValidationError

# ── Logs directory ────────────────────────────────────────────────────────────
LOGDIR = const.LOGS_DIR
if not os.path.exists(LOGDIR):
    os.makedirs(LOGDIR, exist_ok=True)

# ── Logging config ────────────────────────────────────────────────────────────
logging.config.fileConfig(
    const.LOGGING_CONFIG_FILE,
    defaults={"logdir": const.LOGS_DIR},
    disable_existing_loggers=False,
)
logger = logging.getLogger("fastapi.app")


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Order Management System")
    await create_tables_if_not_exist()
    logger.info("Database tables verified/created successfully")
    yield
    logger.info("Shutting down Order Management System")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Order Management System",
    description=(
        "A production-ready FastAPI application.\n\n"
        "## Authentication\n"
        "1. **Register** a user via `POST /api/v1/auth/register`\n"
        "2. **Login** via `POST /api/v1/auth/login` — use your email as *username*\n"
        "3. Click the **Authorize 🔒** button and paste the returned token\n"
        "4. All Order endpoints are now unlocked — you will only see **your own** orders"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ────────────────────────────────────────────────────────
app.add_exception_handler(OrderNotFoundException, order_not_found_exception_handler)
app.add_exception_handler(
    OrderAlreadyExistsException, order_already_exists_exception_handler
)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(api_router)  # /api/v1/auth/... and /api/v1/users/...
app.include_router(order_router)  # /api/orders/...


@app.get("/", tags=["System"])
def welcome():
    logger.info("Welcome endpoint called")
    return {
        "message": "Welcome to Order Management System",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["System"])
def health_check():
    logger.debug("Health check called")
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
