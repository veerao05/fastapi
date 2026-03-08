from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class OrderNotFoundException(Exception):
    """Raised when an order is not found for the given user."""

    def __init__(self, order_id: int):
        self.order_id = order_id
        self.message = f"Order with id {order_id} not found"
        super().__init__(self.message)


class OrderAlreadyExistsException(Exception):
    """Raised when the user already has a pending order for the same product."""

    def __init__(self, product_name: str):
        self.product_name = product_name
        self.message = f"You already have a pending order for '{product_name}'"
        super().__init__(self.message)


# ── Exception handlers ────────────────────────────────────────────────────────


async def order_not_found_exception_handler(
    request: Request,
    exc: OrderNotFoundException,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "message": exc.message,
            "order_id": exc.order_id,
            "path": str(request.url),
        },
    )


async def order_already_exists_exception_handler(
    request: Request,
    exc: OrderAlreadyExistsException,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "Conflict",
            "message": exc.message,
            "product_name": exc.product_name,
            "path": str(request.url),
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid input data",
            "details": exc.errors(),
            "path": str(request.url),
        },
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "details": str(exc),
            "path": str(request.url),
        },
    )
