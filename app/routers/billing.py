from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.models.billing import PaymentMethod, PaymentStatus
from app.schemas.billing import (
    InvoiceOut,
    InvoiceCreate,
    InvoiceUpdate,
    RevenueSummary,
)
from app.schemas.common import PaginatedResponse
from app.auth.dependencies import require_roles, get_current_active_user
from app.crud.billing import (
    get_invoice_by_id,
    create_invoice,
    update_invoice,
    get_invoices_paginated,
    get_revenue_summary,
)
from app.crud.patient import get_patient_by_id
from app.utils.pagination import paginate

router = APIRouter(prefix="/billing", tags=["Billing & Invoices"])


@router.get("/invoices", response_model=PaginatedResponse[InvoiceOut])
async def list_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    patient_id: Optional[int] = None,
    payment_status: Optional[PaymentStatus] = None,
    payment_method: Optional[PaymentMethod] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role == UserRole.PATIENT:
        from app.crud.patient import get_patient_by_user_id
        patient = await get_patient_by_user_id(db, current_user.id)
        if not patient:
            return paginate([], 0, page, page_size)
        patient_id = patient.id

    invoices, total = await get_invoices_paginated(
        db,
        page=page,
        page_size=page_size,
        patient_id=patient_id,
        payment_status=payment_status,
        payment_method=payment_method,
    )
    inv_outs = [InvoiceOut.model_validate(inv) for inv in invoices]
    return paginate(inv_outs, total, page, page_size)


@router.post(
    "/invoices",
    response_model=InvoiceOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.RECEPTIONIST]))],
)
async def create_new_invoice(
    inv_in: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
):
    patient = await get_patient_by_id(db, inv_in.patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return await create_invoice(db, inv_in)


@router.get("/invoices/{invoice_id}", response_model=InvoiceOut)
async def get_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
):
    inv = await get_invoice_by_id(db, invoice_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return inv


@router.patch(
    "/invoices/{invoice_id}",
    response_model=InvoiceOut,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.DOCTOR, UserRole.RECEPTIONIST]))],
)
async def update_existing_invoice(
    invoice_id: int,
    inv_in: InvoiceUpdate,
    db: AsyncSession = Depends(get_db),
):
    inv = await get_invoice_by_id(db, invoice_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return await update_invoice(db, inv, inv_in)


@router.get(
    "/revenue-summary",
    response_model=RevenueSummary,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.DOCTOR, UserRole.RECEPTIONIST]))],
)
async def get_billing_revenue_summary(
    db: AsyncSession = Depends(get_db),
):
    return await get_revenue_summary(db)
