from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import UserRole
from app.schemas.department import (
    DepartmentOut,
    DepartmentCreate,
    DepartmentUpdate,
)
from app.schemas.doctor import DoctorOut
from app.schemas.common import PaginatedResponse
from app.auth.dependencies import require_roles, get_current_active_user
from app.crud.department import (
    get_department_by_id,
    get_department_by_name,
    create_department,
    update_department,
    get_departments_paginated,
    get_doctors_for_department,
)
from app.utils.pagination import paginate

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("/", response_model=PaginatedResponse[DepartmentOut])
async def list_departments(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    departments, total = await get_departments_paginated(db, page=page, page_size=page_size)
    dept_outs = [DepartmentOut.model_validate(d) for d in departments]
    return paginate(dept_outs, total, page, page_size)


@router.post(
    "/",
    response_model=DepartmentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.ADMIN]))],
)
async def create_new_department(
    dept_in: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
):
    existing = await get_department_by_name(db, dept_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Department '{dept_in.name}' already exists",
        )
    return await create_department(db, dept_in)


@router.get("/{department_id}", response_model=DepartmentOut)
async def get_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
):
    dept = await get_department_by_id(db, department_id)
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return dept


@router.patch(
    "/{department_id}",
    response_model=DepartmentOut,
    dependencies=[Depends(require_roles([UserRole.ADMIN]))],
)
async def update_existing_department(
    department_id: int,
    dept_in: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    dept = await get_department_by_id(db, department_id)
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return await update_department(db, dept, dept_in)


@router.get("/{department_id}/doctors", response_model=List[DoctorOut])
async def list_department_doctors(
    department_id: int,
    db: AsyncSession = Depends(get_db),
):
    dept = await get_department_by_id(db, department_id)
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    doctors = await get_doctors_for_department(db, department_id)
    return [DoctorOut.model_validate(doc) for doc in doctors]
