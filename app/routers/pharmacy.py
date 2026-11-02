from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import UserRole
from app.schemas.pharmacy import (
    MedicineOut,
    MedicineCreate,
    MedicineUpdate,
    MedicineBatchOut,
    StockInRequest,
    StockOutRequest,
    InventoryValuationOut,
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.auth.dependencies import require_roles
from app.crud.pharmacy import (
    get_medicine_by_id,
    create_medicine,
    update_medicine,
    get_medicines_paginated,
    stock_in,
    stock_out,
    get_low_stock_medicines,
    get_expiring_batches,
    get_inventory_valuation,
)
from app.utils.pagination import paginate

router = APIRouter(prefix="/pharmacy", tags=["Pharmacy & Inventory"])


@router.get("/medicines", response_model=PaginatedResponse[MedicineOut])
async def list_medicines(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    meds, total = await get_medicines_paginated(
        db,
        page=page,
        page_size=page_size,
        search=search,
        category=category,
    )
    med_outs = [MedicineOut.model_validate(m) for m in meds]
    return paginate(med_outs, total, page, page_size)


@router.post(
    "/medicines",
    response_model=MedicineOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.ADMIN]))],
)
async def create_new_medicine(
    med_in: MedicineCreate,
    db: AsyncSession = Depends(get_db),
):
    med = await create_medicine(db, med_in)
    return MedicineOut.model_validate({
        "id": med.id,
        "name": med.name,
        "generic_name": med.generic_name,
        "category": med.category,
        "unit": med.unit,
        "reorder_level": med.reorder_level,
        "total_stock": 0,
        "is_low_stock": True,
        "batches": [],
        "created_at": med.created_at,
        "updated_at": med.updated_at,
    })


@router.get("/medicines/{medicine_id}", response_model=MedicineOut)
async def get_medicine(
    medicine_id: int,
    db: AsyncSession = Depends(get_db),
):
    med = await get_medicine_by_id(db, medicine_id)
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
    total_stock = sum(b.current_stock for b in med.batches)
    return MedicineOut.model_validate({
        "id": med.id,
        "name": med.name,
        "generic_name": med.generic_name,
        "category": med.category,
        "unit": med.unit,
        "reorder_level": med.reorder_level,
        "total_stock": total_stock,
        "is_low_stock": total_stock <= med.reorder_level,
        "batches": med.batches,
        "created_at": med.created_at,
        "updated_at": med.updated_at,
    })


@router.patch(
    "/medicines/{medicine_id}",
    response_model=MedicineOut,
    dependencies=[Depends(require_roles([UserRole.ADMIN]))],
)
async def update_existing_medicine(
    medicine_id: int,
    med_in: MedicineUpdate,
    db: AsyncSession = Depends(get_db),
):
    med = await get_medicine_by_id(db, medicine_id)
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
    updated = await update_medicine(db, med, med_in)
    total_stock = sum(b.current_stock for b in updated.batches)
    return MedicineOut.model_validate({
        "id": updated.id,
        "name": updated.name,
        "generic_name": updated.generic_name,
        "category": updated.category,
        "unit": updated.unit,
        "reorder_level": updated.reorder_level,
        "total_stock": total_stock,
        "is_low_stock": total_stock <= updated.reorder_level,
        "batches": updated.batches,
        "created_at": updated.created_at,
        "updated_at": updated.updated_at,
    })


@router.post(
    "/stock-in",
    response_model=MedicineBatchOut,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.DOCTOR, UserRole.RECEPTIONIST]))],
)
async def purchase_stock_in(
    req: StockInRequest,
    db: AsyncSession = Depends(get_db),
):
    med = await get_medicine_by_id(db, req.medicine_id)
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
    return await stock_in(db, req)


@router.post(
    "/stock-out",
    response_model=MessageResponse,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.DOCTOR, UserRole.RECEPTIONIST]))],
)
async def dispense_stock_out(
    req: StockOutRequest,
    db: AsyncSession = Depends(get_db),
):
    med = await get_medicine_by_id(db, req.medicine_id)
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
    try:
        qty = await stock_out(db, req)
        return MessageResponse(message=f"Successfully dispensed {qty} units of {med.name}")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/alerts/low-stock")
async def list_low_stock_alerts(
    db: AsyncSession = Depends(get_db),
):
    return await get_low_stock_medicines(db)


@router.get("/alerts/expiring")
async def list_expiring_alerts(
    days: int = Query(30, ge=1, le=180),
    db: AsyncSession = Depends(get_db),
):
    return await get_expiring_batches(db, days=days)


@router.get("/valuation", response_model=InventoryValuationOut)
async def get_pharmacy_valuation(
    db: AsyncSession = Depends(get_db),
):
    return await get_inventory_valuation(db)
