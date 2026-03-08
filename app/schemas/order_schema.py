from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum


class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=200)
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)


class OrderUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1, max_length=200)
    quantity: Optional[int] = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, gt=0)
    status: Optional[OrderStatus] = None


class OrderResponse(BaseModel):
    id: int
    user_id: int
    product_name: str
    quantity: int
    unit_price: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
