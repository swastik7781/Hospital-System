import os
import shutil
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.config import settings
from app.models.user import User, UserRole
from app.models.lab_test import LabTestType, LabTestStatus
from app.schemas.lab_test import (
    LabTestOut,
    LabTestCreate,
    LabTestUpdate,
)
from app.schemas.common import PaginatedResponse
from app.auth.dependencies import require_roles, get_current_active_user
from app.crud.lab_test import (
    get_lab_test_by_id,
    create_lab_test,
    update_lab_test,
    get_lab_tests_paginated,
)
from app.crud.patient import get_patient_by_id
from app.utils.pagination import paginate

router = APIRouter(prefix="/lab-tests", tags=["Lab Tests & Reports"])


@router.get("/", response_model=PaginatedResponse[LabTestOut])
async def list_lab_tests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    test_type: Optional[LabTestType] = None,
    status: Optional[LabTestStatus] = None,
    critical_only: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role == UserRole.PATIENT:
        from app.crud.patient import get_patient_by_user_id
        patient = await get_patient_by_user_id(db, current_user.id)
        if not patient:
            return paginate([], 0, page, page_size)
        patient_id = patient.id

    lab_tests, total = await get_lab_tests_paginated(
        db,
        page=page,
        page_size=page_size,
        patient_id=patient_id,
        doctor_id=doctor_id,
        test_type=test_type,
        status=status,
        critical_only=critical_only,
    )
    test_outs = [LabTestOut.model_validate(t) for t in lab_tests]
    return paginate(test_outs, total, page, page_size)


@router.post(
    "/",
    response_model=LabTestOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.DOCTOR]))],
)
async def order_lab_test(
    lab_in: LabTestCreate,
    db: AsyncSession = Depends(get_db),
):
    patient = await get_patient_by_id(db, lab_in.patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return await create_lab_test(db, lab_in)


@router.get("/{lab_test_id}", response_model=LabTestOut)
async def get_lab_test(
    lab_test_id: int,
    db: AsyncSession = Depends(get_db),
):
    test = await get_lab_test_by_id(db, lab_test_id)
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lab test not found")
    return test


@router.patch(
    "/{lab_test_id}",
    response_model=LabTestOut,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.DOCTOR, UserRole.RECEPTIONIST]))],
)
async def update_lab_test_status(
    lab_test_id: int,
    lab_in: LabTestUpdate,
    db: AsyncSession = Depends(get_db),
):
    test = await get_lab_test_by_id(db, lab_test_id)
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lab test not found")
    return await update_lab_test(db, test, lab_in)


@router.post(
    "/{lab_test_id}/upload-report",
    response_model=LabTestOut,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.DOCTOR]))],
)
async def upload_lab_report_file(
    lab_test_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    test = await get_lab_test_by_id(db, lab_test_id)
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lab test not found")

    ext = os.path.splitext(file.filename)[1]
    safe_name = f"report_{test.id}_{uuid.uuid4().hex[:8]}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    update_in = LabTestUpdate(
        report_file=f"/uploads/{safe_name}",
        status=LabTestStatus.COMPLETED,
    )
    return await update_lab_test(db, test, update_in)
