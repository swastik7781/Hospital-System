from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.prescription import (
    PrescriptionOut,
    PrescriptionCreate,
    PrescriptionUpdate,
)
from app.schemas.common import PaginatedResponse
from app.auth.dependencies import require_roles, get_current_active_user
from app.crud.prescription import (
    get_prescription_by_id,
    create_prescription,
    update_prescription,
    get_prescriptions_paginated,
    get_active_prescriptions_for_patient,
)
from app.crud.patient import get_patient_by_id
from app.services.pdf_service import generate_prescription_pdf
from app.utils.pagination import paginate

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


@router.get("/", response_model=PaginatedResponse[PrescriptionOut])
async def list_prescriptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    visit_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role == UserRole.PATIENT:
        from app.crud.patient import get_patient_by_user_id
        patient = await get_patient_by_user_id(db, current_user.id)
        if not patient:
            return paginate([], 0, page, page_size)
        patient_id = patient.id

    prescriptions, total = await get_prescriptions_paginated(
        db,
        page=page,
        page_size=page_size,
        patient_id=patient_id,
        doctor_id=doctor_id,
        visit_id=visit_id,
    )
    presc_outs = [PrescriptionOut.model_validate(p) for p in prescriptions]
    return paginate(presc_outs, total, page, page_size)


@router.post(
    "/",
    response_model=PrescriptionOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.DOCTOR]))],
)
async def create_new_prescription(
    presc_in: PrescriptionCreate,
    db: AsyncSession = Depends(get_db),
):
    patient = await get_patient_by_id(db, presc_in.patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return await create_prescription(db, presc_in)


@router.get("/{prescription_id}", response_model=PrescriptionOut)
async def get_prescription(
    prescription_id: int,
    db: AsyncSession = Depends(get_db),
):
    presc = await get_prescription_by_id(db, prescription_id)
    if not presc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")
    return presc


@router.patch(
    "/{prescription_id}",
    response_model=PrescriptionOut,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.DOCTOR]))],
)
async def update_existing_prescription(
    prescription_id: int,
    presc_in: PrescriptionUpdate,
    db: AsyncSession = Depends(get_db),
):
    presc = await get_prescription_by_id(db, prescription_id)
    if not presc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")
    return await update_prescription(db, presc, presc_in)


@router.get("/{prescription_id}/pdf")
async def download_prescription_pdf(
    prescription_id: int,
    db: AsyncSession = Depends(get_db),
):
    presc = await get_prescription_by_id(db, prescription_id)
    if not presc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")

    pdf_bytes = generate_prescription_pdf(presc)
    filename = f"prescription_{presc.id}_{presc.prescription_date}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/pdf",
        },
    )


@router.get("/patient/{patient_id}/active", response_model=List[PrescriptionOut])
async def list_active_patient_prescriptions(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    prescriptions = await get_active_prescriptions_for_patient(db, patient_id)
    return [PrescriptionOut.model_validate(p) for p in prescriptions]
