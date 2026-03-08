import logging

from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.order_schema import OrderCreate, OrderResponse, OrderUpdate
from app.services.order_service import OrderService

logger = logging.getLogger("fastapi.app")

router = APIRouter(
    prefix="/api/orders",
    tags=["Orders API"],
    dependencies=[Depends(get_current_user)],
)


async def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(db)


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Place a new order",
    description="Create a new order for the logged-in user.",
)
async def create_order(
    order: OrderCreate,
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user),
):
    logger.info(
        "User %s placing order: product=%s", current_user.email, order.product_name
    )
    result = await service.create_order(current_user.id, order)
    logger.info("Order created with id=%s", result.id)
    return result


@router.get(
    "/",
    response_model=List[OrderResponse],
    summary="List my orders",
    description="Retrieve all orders belonging to the logged-in user.",
)
async def get_my_orders(
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user),
):
    logger.info("Fetching orders for user %s", current_user.email)
    orders = await service.get_orders(current_user.id)
    logger.info("Found %d orders for user %s", len(orders), current_user.email)
    return orders


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order by ID",
    description="Retrieve a specific order by ID. Only returns the order if it belongs to the logged-in user.",
)
async def get_order(
    order_id: int = Path(..., gt=0, description="The ID of the order"),
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user),
):
    logger.info("Fetching order id=%s for user %s", order_id, current_user.email)
    return await service.get_order(order_id, current_user.id)


@router.put(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Update an order",
    description="Update an existing order. Only the owner can update their order.",
)
async def update_order(
    order_update: OrderUpdate,
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user),
    order_id: int = Path(..., gt=0, description="The ID of the order"),
):
    logger.info("Updating order id=%s for user %s", order_id, current_user.email)
    result = await service.update_order(order_id, current_user.id, order_update)
    logger.info("Order id=%s updated", order_id)
    return result


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel / delete an order",
    description="Delete an order permanently. Only the owner can delete their order.",
)
async def delete_order(
    order_id: int = Path(..., gt=0, description="The ID of the order"),
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user),
):
    logger.info("Deleting order id=%s for user %s", order_id, current_user.email)
    await service.delete_order(order_id, current_user.id)
    logger.info("Order id=%s deleted", order_id)
