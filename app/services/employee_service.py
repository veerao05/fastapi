import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.schemas.model_schema import EmployeeCreate, EmployeeUpdate

logger = logging.getLogger("fastapi.app")


class EmployeeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_employee(self, employee_data: EmployeeCreate) -> Employee:
        logger.debug("Validating and creating employee: email=%s", employee_data.email)
        if employee_data.salary and employee_data.salary < 0:
            logger.error("Invalid salary value: %s", employee_data.salary)
            raise ValueError("Salary cannot be negative")

        employee = Employee(**employee_data.model_dump())
        self.db.add(employee)
        await self.db.commit()
        await self.db.refresh(employee)
        logger.debug("Employee persisted to DB with id=%s", employee.id)
        return employee

    async def get_employee(self, employee_id: int) -> Optional[Employee]:
        logger.debug("Querying DB for employee id=%s", employee_id)
        result = await self.db.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        employee = result.scalar_one_or_none()
        if not employee:
            logger.debug("No employee found with id=%s", employee_id)
        return employee

    async def get_employees(self) -> List[Employee]:
        logger.debug("Querying DB for all employees")
        result = await self.db.execute(select(Employee))
        employees = list(result.scalars().all())
        logger.debug("Retrieved %d employees from DB", len(employees))
        return employees

    async def update_employee(self, employee_id: int, employee_data: EmployeeUpdate) -> Optional[Employee]:
        logger.debug("Updating employee id=%s", employee_id)
        employee = await self.get_employee(employee_id)
        if not employee:
            logger.debug("Employee id=%s not found, skipping update", employee_id)
            return None

        update_data = employee_data.model_dump(exclude_unset=True)
        if 'salary' in update_data and update_data['salary'] < 0:
            logger.error("Invalid salary value during update: %s", update_data['salary'])
            raise ValueError("Salary cannot be negative")

        for field, value in update_data.items():
            setattr(employee, field, value)

        await self.db.commit()
        await self.db.refresh(employee)
        logger.debug("Employee id=%s updated successfully", employee_id)
        return employee

    async def delete_employee(self, employee_id: int) -> bool:
        logger.debug("Deleting employee id=%s", employee_id)
        employee = await self.get_employee(employee_id)
        if not employee:
            logger.debug("Employee id=%s not found, skipping delete", employee_id)
            return False

        await self.db.delete(employee)
        await self.db.commit()
        logger.debug("Employee id=%s deleted from DB", employee_id)
        return True