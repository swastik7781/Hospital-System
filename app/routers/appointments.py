from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.models.appointment import AppointmentStatus
from app.schemas.appointment import (
    AppointmentOut,
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentComplete,
)
from app.schemas.common import PaginatedResponse
from app.auth.dependencies import require_roles, get_current_active_user
from app.crud.appointment import (
    get_appointment_by_id,
    check_appointment_conflict,
    create_appointment,
    update_appointment,
    complete_appointment,
    get_appointments_paginated,
)
from app.crud.patient import get_patient_by_id
from app.crud.doctor import get_doctor_by_id
from app.utils.pagination import paginate

router = APIRouter(prefix="/appointments", tags=["Appointments & Visits"])


@router.get("/", response_model=PaginatedResponse[AppointmentOut])
async def list_appointments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    department_id: Optional[int] = None,
    status: Optional[AppointmentStatus] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Role-based restriction: Patient can only view their own appointments
    if current_user.role == UserRole.PATIENT:
        from app.crud.patient import get_patient_by_user_id
        patient = await get_patient_by_user_id(db, current_user.id)
        if not patient:
            return paginate([], 0, page, page_size)
        patient_id = patient.id

    appointments, total = await get_appointments_paginated(
        db,
        page=page,
        page_size=page_size,
        patient_id=patient_id,
        doctor_id=doctor_id,
        department_id=department_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )
    app_outs = [AppointmentOut.model_validate(a) for a in appointments]
    return paginate(app_outs, total, page, page_size)


@router.post(
    "/",
    response_model=AppointmentOut,
    status_code=status.HTTP_201_CREATED,
)
async def book_appointment(
    app_in: AppointmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate patient exists
    patient = await get_patient_by_id(db, app_in.patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # If patient user, ensure booking for self
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot book appointment for another patient")

    # Validate doctor exists
    doctor = await get_doctor_by_id(db, app_in.doctor_id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    # Conflict detection: no double booking for same doctor at same date and time slot
    conflict = await check_appointment_conflict(db, app_in.doctor_id, app_in.appointment_date, app_in.time_slot)
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Doctor is already booked for date {app_in.appointment_date} at slot {app_in.time_slot}",
        )

    appointment = await create_appointment(db, app_in)

    # Auto-generate consultation fee bill in billing
    try:
        from app.crud.billing import create_invoice
        from app.schemas.billing import InvoiceCreate, InvoiceItemCreate
        from app.models.billing import PaymentMethod
        fee = float(doctor.consultation_fee or 800.0)
        await create_invoice(
            db,
            InvoiceCreate(
                patient_id=appointment.patient_id,
                discount=0.0,
                amount_paid=0.0,
                payment_method=PaymentMethod.CASH,
                items=[
                    InvoiceItemCreate(
                        description=f"OPD Consultation — {doctor.full_name} ({doctor.specialization})",
                        quantity=1,
                        unit_price=fee,
                    )
                ],
            ),
        )
    except Exception as e:
        # Log invoice auto-generation exception but keep appointment created
        pass

    return appointment


@router.get("/{appointment_id}", response_model=AppointmentOut)
async def get_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
):
    appointment = await get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return appointment


@router.patch("/{appointment_id}", response_model=AppointmentOut)
async def update_appointment_details(
    appointment_id: int,
    app_in: AppointmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    appointment = await get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    # If rescheduling date or slot, recheck conflict
    new_date = app_in.appointment_date or appointment.appointment_date
    new_slot = app_in.time_slot or appointment.time_slot
    if (app_in.appointment_date or app_in.time_slot) and (new_date != appointment.appointment_date or new_slot != appointment.time_slot):
        conflict = await check_appointment_conflict(
            db, appointment.doctor_id, new_date, new_slot, exclude_id=appointment.id
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Doctor is already booked on {new_date} at slot {new_slot}",
            )

    return await update_appointment(db, appointment, app_in)


@router.post(
    "/{appointment_id}/complete",
    response_model=AppointmentOut,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.DOCTOR, UserRole.RECEPTIONIST]))],
)
async def complete_visit(
    appointment_id: int,
    comp_in: AppointmentComplete,
    db: AsyncSession = Depends(get_db),
):
    appointment = await get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return await complete_appointment(db, appointment, comp_in)
