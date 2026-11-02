from typing import Optional, List, Tuple
from datetime import date
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.patient import Patient
from app.models.appointment import Appointment, AppointmentStatus
from app.models.prescription import Prescription
from app.models.lab_test import LabTest, LabTestStatus
from app.models.billing import Invoice, PaymentStatus
from app.schemas.patient import PatientCreate, PatientUpdate, PatientDashboardSummary


async def get_patient_by_id(db: AsyncSession, patient_id: int, include_deleted: bool = False) -> Optional[Patient]:
    query = select(Patient).where(Patient.id == patient_id)
    if not include_deleted:
        query = query.where(Patient.is_deleted.is_(False))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_patient_by_user_id(db: AsyncSession, user_id: int) -> Optional[Patient]:
    result = await db.execute(select(Patient).where(Patient.user_id == user_id, Patient.is_deleted.is_(False)))
    return result.scalar_one_or_none()


async def create_patient(db: AsyncSession, patient_in: PatientCreate) -> Patient:
    patient = Patient(**patient_in.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


async def update_patient(db: AsyncSession, patient: Patient, patient_in: PatientUpdate) -> Patient:
    update_data = patient_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


async def soft_delete_patient(db: AsyncSession, patient: Patient) -> None:
    patient.is_deleted = True
    db.add(patient)
    await db.commit()


async def get_patients_paginated(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    gender: Optional[str] = None,
    blood_group: Optional[str] = None,
) -> Tuple[List[Patient], int]:
    query = select(Patient).where(Patient.is_deleted.is_(False))

    if search:
        s = f"%{search.lower()}%"
        # Check if search is numeric id
        if search.isdigit():
            query = query.where(
                or_(
                    Patient.id == int(search),
                    func.lower(Patient.full_name).like(s),
                    func.lower(Patient.phone).like(s),
                    func.lower(Patient.email).like(s),
                )
            )
        else:
            query = query.where(
                or_(
                    func.lower(Patient.full_name).like(s),
                    func.lower(Patient.phone).like(s),
                    func.lower(Patient.email).like(s),
                )
            )

    if gender:
        query = query.where(func.lower(Patient.gender) == gender.lower())
    if blood_group:
        query = query.where(Patient.blood_group == blood_group)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    offset = (page - 1) * page_size
    query = query.order_by(Patient.id.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_patient_dashboard_summary(db: AsyncSession, patient: Patient) -> PatientDashboardSummary:
    # Total visits
    visits_res = await db.execute(
        select(func.count(Appointment.id)).where(Appointment.patient_id == patient.id)
    )
    total_visits = visits_res.scalar_one()

    # Active prescriptions (last 30 days)
    presc_res = await db.execute(
        select(func.count(Prescription.id)).where(Prescription.patient_id == patient.id)
    )
    active_prescriptions_count = presc_res.scalar_one()

    # Pending reports
    reports_res = await db.execute(
        select(func.count(LabTest.id)).where(
            LabTest.patient_id == patient.id,
            LabTest.status != LabTestStatus.COMPLETED
        )
    )
    pending_reports_count = reports_res.scalar_one()

    # Unpaid invoices
    inv_res = await db.execute(
        select(func.count(Invoice.id)).where(
            Invoice.patient_id == patient.id,
            Invoice.payment_status != PaymentStatus.PAID
        )
    )
    unpaid_invoices_count = inv_res.scalar_one()

    # Upcoming appointments
    today = date.today()
    upcoming_res = await db.execute(
        select(Appointment)
        .options(selectinload(Appointment.doctor))
        .where(
            Appointment.patient_id == patient.id,
            Appointment.appointment_date >= today,
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
        )
        .order_by(Appointment.appointment_date.asc())
        .limit(5)
    )
    upcoming_list = [
        {
            "id": a.id,
            "date": str(a.appointment_date),
            "time_slot": a.time_slot,
            "doctor": a.doctor.full_name if a.doctor else "Unknown",
            "reason": a.reason,
            "status": a.status.value,
        }
        for a in upcoming_res.scalars().all()
    ]

    # Recent prescriptions
    rec_presc_res = await db.execute(
        select(Prescription)
        .options(selectinload(Prescription.doctor), selectinload(Prescription.items))
        .where(Prescription.patient_id == patient.id)
        .order_by(Prescription.prescription_date.desc())
        .limit(5)
    )
    recent_presc_list = [
        {
            "id": p.id,
            "date": str(p.prescription_date),
            "doctor": p.doctor.full_name if p.doctor else "Unknown",
            "instructions": p.instructions,
            "items_count": len(p.items),
        }
        for p in rec_presc_res.scalars().all()
    ]

    # Recent reports
    rec_rep_res = await db.execute(
        select(LabTest)
        .where(LabTest.patient_id == patient.id)
        .order_by(LabTest.scheduled_date.desc())
        .limit(5)
    )
    recent_rep_list = [
        {
            "id": r.id,
            "test_type": r.test_type.value,
            "scheduled_date": str(r.scheduled_date),
            "status": r.status.value,
            "critical_value": r.critical_value,
            "findings": r.findings,
        }
        for r in rec_rep_res.scalars().all()
    ]

    return PatientDashboardSummary(
        patient_id=patient.id,
        full_name=patient.full_name,
        total_visits=total_visits,
        active_prescriptions_count=active_prescriptions_count,
        pending_reports_count=pending_reports_count,
        unpaid_invoices_count=unpaid_invoices_count,
        upcoming_appointments=upcoming_list,
        recent_prescriptions=recent_presc_list,
        recent_reports=recent_rep_list,
    )
