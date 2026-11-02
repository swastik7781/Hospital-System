from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.lab_test import LabTest, LabTestType, LabTestStatus
from app.models.doctor import Doctor
from app.schemas.lab_test import LabTestCreate, LabTestUpdate


async def get_lab_test_by_id(db: AsyncSession, lab_test_id: int) -> Optional[LabTest]:
    result = await db.execute(
        select(LabTest)
        .options(
            selectinload(LabTest.patient),
            selectinload(LabTest.doctor).selectinload(Doctor.department),
        )
        .where(LabTest.id == lab_test_id)
    )
    return result.scalar_one_or_none()


async def create_lab_test(db: AsyncSession, lab_in: LabTestCreate) -> LabTest:
    lab_test = LabTest(**lab_in.model_dump())
    db.add(lab_test)
    await db.commit()
    await db.refresh(lab_test)
    return await get_lab_test_by_id(db, lab_test.id)


async def update_lab_test(db: AsyncSession, lab_test: LabTest, lab_in: LabTestUpdate) -> LabTest:
    update_data = lab_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lab_test, field, value)
    db.add(lab_test)
    await db.commit()
    await db.refresh(lab_test)
    return await get_lab_test_by_id(db, lab_test.id)


async def get_lab_tests_paginated(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    test_type: Optional[LabTestType] = None,
    status: Optional[LabTestStatus] = None,
    critical_only: Optional[bool] = None,
) -> Tuple[List[LabTest], int]:
    query = select(LabTest).options(
        selectinload(LabTest.patient),
        selectinload(LabTest.doctor).selectinload(Doctor.department),
    )

    if patient_id is not None:
        query = query.where(LabTest.patient_id == patient_id)
    if doctor_id is not None:
        query = query.where(LabTest.doctor_id == doctor_id)
    if test_type is not None:
        query = query.where(LabTest.test_type == test_type)
    if status is not None:
        query = query.where(LabTest.status == status)
    if critical_only:
        query = query.where(LabTest.critical_value.is_(True))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    offset = (page - 1) * page_size
    query = query.order_by(LabTest.scheduled_date.desc(), LabTest.id.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total
