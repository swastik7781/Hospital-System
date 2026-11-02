from typing import Optional, List, Tuple
from datetime import date, timedelta
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.prescription import Prescription, PrescriptionItem
from app.models.doctor import Doctor
from app.schemas.prescription import PrescriptionCreate, PrescriptionUpdate


async def get_prescription_by_id(db: AsyncSession, prescription_id: int) -> Optional[Prescription]:
    result = await db.execute(
        select(Prescription)
        .options(
            selectinload(Prescription.patient),
            selectinload(Prescription.doctor).selectinload(Doctor.department),
            selectinload(Prescription.items),
        )
        .where(Prescription.id == prescription_id)
    )
    return result.scalar_one_or_none()


async def create_prescription(db: AsyncSession, presc_in: PrescriptionCreate) -> Prescription:
    presc_data = presc_in.model_dump(exclude={"items"})
    prescription = Prescription(**presc_data)
    db.add(prescription)
    await db.flush()  # assign prescription.id

    for item_in in presc_in.items:
        item = PrescriptionItem(
            prescription_id=prescription.id,
            **item_in.model_dump()
        )
        db.add(item)

    await db.commit()
    return await get_prescription_by_id(db, prescription.id)


async def update_prescription(db: AsyncSession, prescription: Prescription, presc_in: PrescriptionUpdate) -> Prescription:
    if presc_in.instructions is not None:
        prescription.instructions = presc_in.instructions

    if presc_in.items is not None:
        # Remove old items
        for old_item in prescription.items:
            await db.delete(old_item)
        # Add new items
        for item_in in presc_in.items:
            item = PrescriptionItem(
                prescription_id=prescription.id,
                **item_in.model_dump()
            )
            db.add(item)

    db.add(prescription)
    await db.commit()
    return await get_prescription_by_id(db, prescription.id)


async def get_prescriptions_paginated(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    visit_id: Optional[int] = None,
) -> Tuple[List[Prescription], int]:
    query = select(Prescription).options(
        selectinload(Prescription.patient),
        selectinload(Prescription.doctor).selectinload(Doctor.department),
        selectinload(Prescription.items),
    )

    if patient_id is not None:
        query = query.where(Prescription.patient_id == patient_id)
    if doctor_id is not None:
        query = query.where(Prescription.doctor_id == doctor_id)
    if visit_id is not None:
        query = query.where(Prescription.visit_id == visit_id)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    offset = (page - 1) * page_size
    query = query.order_by(Prescription.prescription_date.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_active_prescriptions_for_patient(db: AsyncSession, patient_id: int) -> List[Prescription]:
    # Prescriptions in the last 30 days are considered active
    thirty_days_ago = date.today() - timedelta(days=30)
    result = await db.execute(
        select(Prescription)
        .options(
            selectinload(Prescription.patient),
            selectinload(Prescription.doctor).selectinload(Doctor.department),
            selectinload(Prescription.items),
        )
        .where(
            Prescription.patient_id == patient_id,
            Prescription.prescription_date >= thirty_days_ago,
        )
        .order_by(Prescription.prescription_date.desc())
    )
    return list(result.scalars().all())
