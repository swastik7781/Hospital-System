from typing import Optional, List, Tuple
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate


async def get_doctor_by_id(db: AsyncSession, doctor_id: int) -> Optional[Doctor]:
    result = await db.execute(
        select(Doctor)
        .options(selectinload(Doctor.department))
        .where(Doctor.id == doctor_id)
    )
    return result.scalar_one_or_none()


async def get_doctor_by_user_id(db: AsyncSession, user_id: int) -> Optional[Doctor]:
    result = await db.execute(
        select(Doctor)
        .options(selectinload(Doctor.department))
        .where(Doctor.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_doctor(db: AsyncSession, doc_in: DoctorCreate) -> Doctor:
    doc = Doctor(**doc_in.model_dump())
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return await get_doctor_by_id(db, doc.id)  # Load relationships


async def update_doctor(db: AsyncSession, doctor: Doctor, doc_in: DoctorUpdate) -> Doctor:
    update_data = doc_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doctor, field, value)
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)
    return await get_doctor_by_id(db, doctor.id)


async def get_doctors_paginated(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    department_id: Optional[int] = None,
    specialization: Optional[str] = None,
    query_str: Optional[str] = None,
) -> Tuple[List[Doctor], int]:
    query = select(Doctor).options(selectinload(Doctor.department))

    if department_id is not None:
        query = query.where(Doctor.department_id == department_id)
    if specialization:
        query = query.where(func.lower(Doctor.specialization).contains(specialization.lower()))
    if query_str:
        q = f"%{query_str.lower()}%"
        query = query.where(
            or_(
                func.lower(Doctor.full_name).like(q),
                func.lower(Doctor.qualification).like(q),
                func.lower(Doctor.email).like(q),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    offset = (page - 1) * page_size
    query = query.order_by(Doctor.full_name.asc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total
