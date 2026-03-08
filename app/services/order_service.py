import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.schemas.order_schema import OrderCreate, OrderUpdate
from app.utils.exceptions import OrderNotFoundException, OrderAlreadyExistsException

logger = logging.getLogger("fastapi.app")


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, user_id: int, order_data: OrderCreate) -> Order:
        logger.debug(
            "Creating order for user_id=%s product=%s", user_id, order_data.product_name
        )

        # Prevent duplicate pending orders for the same product
        existing = await self.db.execute(
            select(Order).where(
                Order.user_id == user_id,
                Order.product_name == order_data.product_name,
                Order.status == "pending",
            )
        )
        if existing.scalar_one_or_none():
            logger.warning(
                "Duplicate pending order for user_id=%s product=%s",
                user_id,
                order_data.product_name,
            )
            raise OrderAlreadyExistsException(order_data.product_name)

        order = Order(user_id=user_id, **order_data.model_dump())
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        logger.debug("Order created with id=%s", order.id)
        return order

    async def get_orders(self, user_id: int) -> List[Order]:
        logger.debug("Fetching all orders for user_id=%s", user_id)
        result = await self.db.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_order(self, order_id: int, user_id: int) -> Order:
        logger.debug("Fetching order id=%s for user_id=%s", order_id, user_id)
        result = await self.db.execute(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            logger.warning("Order id=%s not found for user_id=%s", order_id, user_id)
            raise OrderNotFoundException(order_id)
        return order

    async def update_order(
        self, order_id: int, user_id: int, order_data: OrderUpdate
    ) -> Order:
        logger.debug("Updating order id=%s for user_id=%s", order_id, user_id)
        order = await self.get_order(
            order_id, user_id
        )  # raises OrderNotFoundException if missing

        for field, value in order_data.model_dump(exclude_unset=True).items():
            setattr(order, field, value)

        await self.db.commit()
        await self.db.refresh(order)
        logger.debug("Order id=%s updated successfully", order_id)
        return order

    async def delete_order(self, order_id: int, user_id: int) -> None:
        logger.debug("Deleting order id=%s for user_id=%s", order_id, user_id)
        order = await self.get_order(
            order_id, user_id
        )  # raises OrderNotFoundException if missing

        await self.db.delete(order)
        await self.db.commit()
        logger.debug("Order id=%s deleted", order_id)
