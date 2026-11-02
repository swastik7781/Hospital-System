from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.department import Department
from app.models.doctor import Doctor
from app.schemas.department import DepartmentCreate, DepartmentUpdate


async def get_department_by_id(db: AsyncSession, department_id: int) -> Optional[Department]:
    result = await db.execute(select(Department).where(Department.id == department_id))
    return result.scalar_one_or_none()


async def get_department_by_name(db: AsyncSession, name: str) -> Optional[Department]:
    result = await db.execute(select(Department).where(func.lower(Department.name) == name.lower()))
    return result.scalar_one_or_none()


async def create_department(db: AsyncSession, dep_in: DepartmentCreate) -> Department:
    dept = Department(**dep_in.model_dump())
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept


async def update_department(db: AsyncSession, dept: Department, dep_in: DepartmentUpdate) -> Department:
    update_data = dep_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dept, field, value)
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept


async def get_departments_paginated(
    db: AsyncSession, page: int = 1, page_size: int = 50
) -> Tuple[List[Department], int]:
    query = select(Department)
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    offset = (page - 1) * page_size
    query = query.order_by(Department.name.asc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_doctors_for_department(db: AsyncSession, department_id: int) -> List[Doctor]:
    result = await db.execute(select(Doctor).where(Doctor.department_id == department_id))
    return list(result.scalars().all())
