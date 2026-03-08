import logging

from fastapi import APIRouter, Depends, Form, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password, create_access_token, hash_password
from app.db.database import get_db
from app.models.user import User

logger = logging.getLogger("fastapi.app")

router = APIRouter(tags=["Auth"])


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginForm:
    """Custom form — only exposes username and password in Swagger UI."""

    def __init__(
        self,
        username: str = Form(..., description="Your registered email address"),
        password: str = Form(...),
    ):
        self.username = username
        self.password = password


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_byte_length(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 characters")
        return v


@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Use your **email as username** and password to get a Bearer token. "
    "Click **Authorize 🔒** at the top of this page to store the token for all requests.",
)
async def login(
    form_data: LoginForm = Depends(),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("Login failed — user not found: %s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    try:
        password_ok = verify_password(form_data.password, user.hashed_password)
    except Exception as e:
        logger.error("Password verification error for %s: %s", form_data.username, e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    if not password_ok:
        logger.warning("Login failed — wrong password for: %s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    logger.info("User logged in: %s", user.email)
    return Token(access_token=create_access_token(sub=user.email))


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    data: RegisterRequest,
    session: AsyncSession = Depends(get_db),
):
    existing = await session.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=data.email, hashed_password=hash_password(data.password))
    session.add(user)
    await session.commit()
    logger.info("New user registered: %s", data.email)
    return {"id": user.id, "email": user.email}
