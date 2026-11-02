from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.doctor import (
    DoctorOut,
    DoctorCreate,
    DoctorUpdate,
    DoctorScheduleOut,
)
from app.schemas.common import PaginatedResponse
from app.auth.dependencies import require_roles, get_current_active_user
from app.crud.doctor import (
    get_doctor_by_id,
    create_doctor,
    update_doctor,
    get_doctors_paginated,
)
from app.crud.department import get_department_by_id
from app.utils.pagination import paginate

router = APIRouter(prefix="/doctors", tags=["Doctors"])


def calculate_time_slots(start_str: str, end_str: str, slot_minutes: int = 30) -> List[str]:
    slots = []
    try:
        t_start = datetime.strptime(start_str, "%H:%M")
        t_end = datetime.strptime(end_str, "%H:%M")
        curr = t_start
        while curr + timedelta(minutes=slot_minutes) <= t_end:
            slots.append(curr.strftime("%H:%M"))
            curr += timedelta(minutes=slot_minutes)
    except Exception:
        slots = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00", "15:30", "16:00"]
    return slots


@router.get("/", response_model=PaginatedResponse[DoctorOut])
async def list_doctors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    department_id: Optional[int] = None,
    specialization: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    doctors, total = await get_doctors_paginated(
        db,
        page=page,
        page_size=page_size,
        department_id=department_id,
        specialization=specialization,
        query_str=search,
    )
    doc_outs = [DoctorOut.model_validate(d) for d in doctors]
    return paginate(doc_outs, total, page, page_size)


@router.post(
    "/",
    response_model=DoctorOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.ADMIN]))],
)
async def create_new_doctor(
    doc_in: DoctorCreate,
    db: AsyncSession = Depends(get_db),
):
    # Verify department exists
    dept = await get_department_by_id(db, doc_in.department_id)
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department does not exist")
    return await create_doctor(db, doc_in)


@router.get("/{doctor_id}", response_model=DoctorOut)
async def get_doctor(
    doctor_id: int,
    db: AsyncSession = Depends(get_db),
):
    doc = await get_doctor_by_id(db, doctor_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return doc


@router.patch(
    "/{doctor_id}",
    response_model=DoctorOut,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.DOCTOR]))],
)
async def update_existing_doctor(
    doctor_id: int,
    doc_in: DoctorUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await get_doctor_by_id(db, doctor_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    # If role is doctor, make sure they are editing their own profile
    if current_user.role == UserRole.DOCTOR and doc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot edit another doctor's profile")
    return await update_doctor(db, doc, doc_in)


@router.get("/{doctor_id}/schedule", response_model=DoctorScheduleOut)
async def get_doctor_schedule(
    doctor_id: int,
    db: AsyncSession = Depends(get_db),
):
    doc = await get_doctor_by_id(db, doctor_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    
    slots = calculate_time_slots(doc.working_hours_start, doc.working_hours_end)
    return DoctorScheduleOut(
        doctor_id=doc.id,
        doctor_name=doc.full_name,
        specialization=doc.specialization,
        department_name=doc.department.name if doc.department else "General",
        available_days=doc.available_days,
        working_hours_start=doc.working_hours_start,
        working_hours_end=doc.working_hours_end,
        time_slots=slots,
    )
