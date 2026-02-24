import logging.config
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
import uvicorn
from starlette.middleware.cors import CORSMiddleware

from app.api.employee_api import router as model_router
from app.db.database import create_tables_if_not_exist
from app.middleware import LoggingMiddleware
import app.utils.constants as const

# ── Ensure logs directory exists before loading logging config ──────────────
LOGDIR = const.LOGS_DIR
if not os.path.exists(LOGDIR):
    os.makedirs(LOGDIR, exist_ok=True)

# ── Load logging configuration ───────────────────────────────────────────────
logging.config.fileConfig(const.LOGGING_CONFIG_FILE, disable_existing_loggers=False)
logger = logging.getLogger("fastapi.app")

# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Employee Management System")
    await create_tables_if_not_exist()
    logger.info("Database tables verified/created successfully")
    yield
    logger.info("Shutting down Employee Management System")


# ── App setup ────────────────────────────────────────────────────────────────
router = APIRouter()

app = FastAPI(
    title="Employee Management System",
    description="A demo FastAPI application with SQLite database",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(model_router)


@app.get("/")
def welcome():
    logger.info("Welcome endpoint called")
    return {
        "message": "Welcome to Employee Management System",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
def health_check():
    logger.debug("Health check endpoint called")
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)