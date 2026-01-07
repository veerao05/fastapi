from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.schemas.model_schema import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_employee(self, employee_data: EmployeeCreate) -> Employee:
        if employee_data.salary and employee_data.salary < 0:
            raise ValueError("Salary cannot be negative")
        
        employee = Employee(**employee_data.model_dump())
        self.db.add(employee)
        await self.db.commit()
        await self.db.refresh(employee)
        return employee
    
    async def get_employee(self, employee_id: int) -> Optional[Employee]:
        result = await self.db.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        return result.scalar_one_or_none()
    
    async def get_employees(self) -> List[Employee]:
        result = await self.db.execute(select(Employee))
        return list(result.scalars().all())
    
    async def update_employee(self, employee_id: int, employee_data: EmployeeUpdate) -> Optional[Employee]:
        employee = await self.get_employee(employee_id)
        if not employee:
            return None
        
        update_data = employee_data.model_dump(exclude_unset=True)
        if 'salary' in update_data and update_data['salary'] < 0:
            raise ValueError("Salary cannot be negative")
        
        for field, value in update_data.items():
            setattr(employee, field, value)
        
        await self.db.commit()
        await self.db.refresh(employee)
        return employee
    
    async def delete_employee(self, employee_id: int) -> bool:
        employee = await self.get_employee(employee_id)
        if not employee:
            return False
        
        await self.db.delete(employee)
        await self.db.commit()
        return True
