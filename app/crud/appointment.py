from typing import Optional, List, Tuple
from datetime import date, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.appointment import Appointment, AppointmentStatus
from app.models.doctor import Doctor
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentComplete


async def get_appointment_by_id(db: AsyncSession, appointment_id: int) -> Optional[Appointment]:
    result = await db.execute(
        select(Appointment)
        .options(
            selectinload(Appointment.patient),
            selectinload(Appointment.doctor).selectinload(Doctor.department),
        )
        .where(Appointment.id == appointment_id)
    )
    return result.scalar_one_or_none()


async def check_appointment_conflict(
    db: AsyncSession, doctor_id: int, appointment_date: date, time_slot: str, exclude_id: Optional[int] = None
) -> bool:
    query = select(func.count(Appointment.id)).where(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
        Appointment.time_slot == time_slot,
        Appointment.status.notin_([AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW]),
    )
    if exclude_id:
        query = query.where(Appointment.id != exclude_id)
    result = await db.execute(query)
    count = result.scalar_one()
    return count > 0


async def create_appointment(db: AsyncSession, app_in: AppointmentCreate) -> Appointment:
    app = Appointment(**app_in.model_dump())
    db.add(app)
    await db.commit()
    await db.refresh(app)

    # Handle recurring bookings if requested (e.g., generate 3 subsequent visits)
    if app_in.is_recurring and app_in.recurrence_pattern:
        pattern = app_in.recurrence_pattern.lower()
        delta_days = 7 if "week" in pattern else 30
        for i in range(1, 4):
            next_date = app_in.appointment_date + timedelta(days=delta_days * i)
            conflict = await check_appointment_conflict(db, app_in.doctor_id, next_date, app_in.time_slot)
            if not conflict:
                recur_app = Appointment(
                    patient_id=app_in.patient_id,
                    doctor_id=app_in.doctor_id,
                    appointment_date=next_date,
                    time_slot=app_in.time_slot,
                    reason=f"{app_in.reason} (Recurring follow-up #{i})",
                    status=AppointmentStatus.SCHEDULED,
                    is_recurring=True,
                    recurrence_pattern=app_in.recurrence_pattern,
                )
                db.add(recur_app)
        await db.commit()

    return await get_appointment_by_id(db, app.id)


async def update_appointment(db: AsyncSession, appointment: Appointment, app_in: AppointmentUpdate) -> Appointment:
    update_data = app_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(appointment, field, value)
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return await get_appointment_by_id(db, appointment.id)


async def complete_appointment(db: AsyncSession, appointment: Appointment, comp_in: AppointmentComplete) -> Appointment:
    appointment.status = AppointmentStatus.COMPLETED
    appointment.diagnosis = comp_in.diagnosis
    if comp_in.notes is not None:
        appointment.notes = comp_in.notes
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return await get_appointment_by_id(db, appointment.id)


async def get_appointments_paginated(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    department_id: Optional[int] = None,
    status: Optional[AppointmentStatus] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> Tuple[List[Appointment], int]:
    query = select(Appointment).options(
        selectinload(Appointment.patient),
        selectinload(Appointment.doctor).selectinload(Doctor.department),
    )

    if patient_id is not None:
        query = query.where(Appointment.patient_id == patient_id)
    if doctor_id is not None:
        query = query.where(Appointment.doctor_id == doctor_id)
    if status is not None:
        query = query.where(Appointment.status == status)
    if date_from is not None:
        query = query.where(Appointment.appointment_date >= date_from)
    if date_to is not None:
        query = query.where(Appointment.appointment_date <= date_to)
    if department_id is not None:
        query = query.join(Doctor, Appointment.doctor_id == Doctor.id).where(Doctor.department_id == department_id)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    offset = (page - 1) * page_size
    query = query.order_by(Appointment.appointment_date.desc(), Appointment.time_slot.asc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total
