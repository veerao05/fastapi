from fastapi import FastAPI, APIRouter
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from app.api.employee_api import router as model_router
from app.db.database import create_tables_if_not_exist

router = APIRouter()


app = FastAPI(
    title="Employee Management System",
    description="A demo FastAPI application with SQLite database",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    await create_tables_if_not_exist()


app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
# Adding the pagination middleware to the FastAPI app

app.include_router(
        model_router
    )

@app.get("/")
def welcome():
    return {
        "message": "Welcome to Employee Management System",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)