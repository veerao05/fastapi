import logging

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.schemas.model_schema import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.employee_service import EmployeeService

logger = logging.getLogger("fastapi.app")

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
    logger.info("Creating new employee with email=%s", employee.email)
    result = await service.create_employee(employee)
    logger.info("Employee created successfully with id=%s", result.id)
    return result


@router.get(
    "/",
    response_model=List[EmployeeResponse],
    summary="Get all employees",
    description="Retrieve all employees"
)
async def get_all_employees(
    service: EmployeeService = Depends(get_employee_service)
):
    logger.info("Fetching all employees")
    employees = await service.get_employees()
    logger.info("Fetched %d employees", len(employees))
    return employees


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
    logger.info("Fetching employee with id=%s", employee_id)
    employee = await service.get_employee(employee_id)
    if not employee:
        logger.warning("Employee not found with id=%s", employee_id)
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
    logger.info("Updating employee with id=%s", employee_id)
    employee = await service.update_employee(employee_id, employee_update)
    if not employee:
        logger.warning("Employee not found for update with id=%s", employee_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    logger.info("Employee updated successfully with id=%s", employee_id)
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
    logger.info("Deleting employee with id=%s", employee_id)
    success = await service.delete_employee(employee_id)
    if not success:
        logger.warning("Employee not found for deletion with id=%s", employee_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    logger.info("Employee deleted successfully with id=%s", employee_id)