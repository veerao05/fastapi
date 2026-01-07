from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.schemas.model_schema import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.employee_service import EmployeeService

router = APIRouter(
    prefix="/api/employees",
    tags=["Employees API"]
)


async def get_employee_service(db: AsyncSession = Depends(get_db)) -> EmployeeService:
    """Dependency injection: Get employee service instance"""
    return EmployeeService(db)


@router.post(
    "/", 
    response_model=EmployeeResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee",
    description="Create a new employee record with validation rules applied"
)
async def create_employee(
    employee: EmployeeCreate, 
    service: EmployeeService = Depends(get_employee_service)
):
    """
    Create a new employee with the following validations:
    
    - **name**: Employee full name (1-100 characters)
    - **email**: Unique email address (must be valid email format)
    - **department**: Department name (1-50 characters, will be normalized to Title Case)
    - **salary**: Annual salary (must be positive)
    """
    return await service.create_employee(employee)


@router.get(
    "/", 
    response_model=List[EmployeeResponse],
    summary="Get all employees",
    description="Retrieve all employees"
)
async def get_all_employees(
    service: EmployeeService = Depends(get_employee_service)
):
    return await service.get_employees()


@router.get(
    "/{employee_id}", 
    response_model=EmployeeResponse,
    summary="Get employee by ID",
    description="Retrieve a specific employee by their ID"
)
async def get_employee_by_id(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service)
):
    """
    Get a specific employee by ID.
    
    - **employee_id**: The unique identifier of the employee
    
    Returns 404 if employee not found.
    """
    employee = await service.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@router.put(
    "/{employee_id}", 
    response_model=EmployeeResponse,
    summary="Update an employee",
    description="Update an existing employee's information"
)
async def update_employee(
    employee_id: int, 
    employee_update: EmployeeUpdate,
    service: EmployeeService = Depends(get_employee_service)
):
    """
    Update an existing employee. Only provided fields will be updated.
    
    - **employee_id**: The ID of the employee to update
    - All fields in request body are optional
    
    Returns 404 if employee not found.
    """
    employee = await service.update_employee(employee_id, employee_update)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@router.delete(
    "/{employee_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an employee",
    description="Permanently delete an employee record"
)
async def delete_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service)
):
    """
    Delete an employee permanently.
    
    - **employee_id**: The ID of the employee to delete
    
    Returns 204 No Content on success.
    Returns 404 if employee not found.
    
    **Warning**: This action cannot be undone.
    """
    success = await service.delete_employee(employee_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

