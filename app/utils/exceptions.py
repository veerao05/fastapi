from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class EmployeeNotFoundException(Exception):
    """Exception raised when employee is not found"""
    
    def __init__(self, employee_id: int):
        self.employee_id = employee_id
        self.message = f"Employee with id {employee_id} not found"
        super().__init__(self.message)


class EmployeeAlreadyExistsException(Exception):
    """Exception raised when employee with email already exists"""
    
    def __init__(self, email: str):
        self.email = email
        self.message = f"Employee with email {email} already exists"
        super().__init__(self.message)


class InvalidSalaryException(Exception):
    """Exception raised when salary validation fails"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


# Custom exception handlers
async def employee_not_found_exception_handler(
    request: Request, 
    exc: EmployeeNotFoundException
) -> JSONResponse:
    """Handler for EmployeeNotFoundException"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "message": exc.message,
            "employee_id": exc.employee_id,
            "path": str(request.url)
        }
    )


async def employee_already_exists_exception_handler(
    request: Request, 
    exc: EmployeeAlreadyExistsException
) -> JSONResponse:
    """Handler for EmployeeAlreadyExistsException"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request",
            "message": exc.message,
            "email": exc.email,
            "path": str(request.url)
        }
    )


async def invalid_salary_exception_handler(
    request: Request, 
    exc: InvalidSalaryException
) -> JSONResponse:
    """Handler for InvalidSalaryException"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Invalid Salary",
            "message": exc.message,
            "path": str(request.url)
        }
    )


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """Handler for request validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid input data",
            "details": exc.errors(),
            "path": str(request.url)
        }
    )


async def generic_exception_handler(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    """Handler for generic exceptions"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "details": str(exc),
            "path": str(request.url)
        }
    )
