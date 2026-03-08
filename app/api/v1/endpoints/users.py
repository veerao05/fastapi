import logging

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserRead

logger = logging.getLogger("fastapi.app")

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user",
    description="Returns the profile of the currently authenticated user.",
)
async def me(current_user: User = Depends(get_current_user)):
    logger.info("User fetched own profile: %s", current_user.email)
    return current_user
