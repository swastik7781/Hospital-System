from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.models.appointment import AppointmentStatus
from app.schemas.patient import (
    PatientOut,
    PatientCreate,
    PatientUpdate,
    PatientDashboardSummary,
    PatientPortalAccountCreate,
    PatientPortalAccountDirectoryItem,
)
from app.schemas.appointment import AppointmentOut
from app.schemas.common import PaginatedResponse, MessageResponse
from app.auth.dependencies import require_roles, get_current_active_user
from app.crud.patient import (
    get_patient_by_id,
    create_patient,
    update_patient,
    soft_delete_patient,
    get_patients_paginated,
    get_patient_dashboard_summary,
    create_or_link_patient_portal_account,
    get_all_patients_portal_directory,
)
from app.crud.appointment import get_appointments_paginated
from app.utils.pagination import paginate

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get(
    "/portal-accounts/directory",
    response_model=List[PatientPortalAccountDirectoryItem],
)
async def list_portal_accounts_directory(
    db: AsyncSession = Depends(get_db),
):
    """Retrieve full directory of all patient EHR accounts with their login emails and IDs."""
    return await get_all_patients_portal_directory(db)


@router.get(
    "/",
    response_model=PaginatedResponse[PatientOut],
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.DOCTOR, UserRole.RECEPTIONIST]))],
)
async def list_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    gender: Optional[str] = None,
    blood_group: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    patients, total = await get_patients_paginated(
        db,
        page=page,
        page_size=page_size,
        search=search,
        gender=gender,
        blood_group=blood_group,
    )
    patient_outs = [PatientOut.model_validate(p) for p in patients]
    return paginate(patient_outs, total, page, page_size)


@router.post(
    "/",
    response_model=PatientOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.RECEPTIONIST]))],
)
async def register_patient(
    patient_in: PatientCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_patient(db, patient_in)


@router.post(
    "/{patient_id}/portal-account",
    response_model=PatientOut,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.RECEPTIONIST]))],
)
async def create_patient_portal_login(
    patient_id: int,
    account_in: PatientPortalAccountCreate,
    db: AsyncSession = Depends(get_db),
):
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    await create_or_link_patient_portal_account(
        db,
        patient,
        password=account_in.password or "patient123",
        email=account_in.email,
    )
    return patient


@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # If role is patient, ensure accessing their own record
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to patient profile")

    return patient


@router.patch(
    "/{patient_id}",
    response_model=PatientOut,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.DOCTOR, UserRole.RECEPTIONIST]))],
)
async def update_patient_record(
    patient_id: int,
    patient_in: PatientUpdate,
    db: AsyncSession = Depends(get_db),
):
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return await update_patient(db, patient, patient_in)


@router.delete(
    "/{patient_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.RECEPTIONIST]))],
)
async def delete_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    await soft_delete_patient(db, patient)
    return MessageResponse(message=f"Patient #{patient_id} soft deleted successfully")


@router.get("/{patient_id}/dashboard", response_model=PatientDashboardSummary)
async def get_patient_dashboard(
    patient_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return await get_patient_dashboard_summary(db, patient)


@router.get("/{patient_id}/visits", response_model=PaginatedResponse[AppointmentOut])
async def get_patient_visits_history(
    patient_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    doctor_id: Optional[int] = None,
    status: Optional[AppointmentStatus] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    visits, total = await get_appointments_paginated(
        db,
        page=page,
        page_size=page_size,
        patient_id=patient_id,
        doctor_id=doctor_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )
    visit_outs = [AppointmentOut.model_validate(v) for v in visits]
    return paginate(visit_outs, total, page, page_size)
