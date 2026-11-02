from typing import Optional, List, Tuple
from datetime import date, timedelta
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pharmacy import Medicine, MedicineBatch, StockMovement
from app.schemas.pharmacy import (
    MedicineCreate,
    MedicineUpdate,
    StockInRequest,
    StockOutRequest,
    InventoryValuationOut,
)


async def get_medicine_by_id(db: AsyncSession, medicine_id: int) -> Optional[Medicine]:
    result = await db.execute(
        select(Medicine)
        .options(selectinload(Medicine.batches))
        .where(Medicine.id == medicine_id)
    )
    return result.scalar_one_or_none()


async def create_medicine(db: AsyncSession, med_in: MedicineCreate) -> Medicine:
    med = Medicine(**med_in.model_dump())
    db.add(med)
    await db.commit()
    await db.refresh(med)
    return await get_medicine_by_id(db, med.id)


async def update_medicine(db: AsyncSession, medicine: Medicine, med_in: MedicineUpdate) -> Medicine:
    update_data = med_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(medicine, field, value)
    db.add(medicine)
    await db.commit()
    await db.refresh(medicine)
    return await get_medicine_by_id(db, medicine.id)


async def get_medicines_paginated(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    category: Optional[str] = None,
) -> Tuple[List[dict], int]:
    query = select(Medicine).options(selectinload(Medicine.batches))

    if search:
        s = f"%{search.lower()}%"
        query = query.where(
            or_(
                func.lower(Medicine.name).like(s),
                func.lower(Medicine.generic_name).like(s),
            )
        )
    if category:
        query = query.where(func.lower(Medicine.category) == category.lower())

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    offset = (page - 1) * page_size
    query = query.order_by(Medicine.name.asc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    medicines = result.scalars().all()

    # Calculate total stock and low stock flag dynamically
    med_list = []
    for m in medicines:
        total_stock = sum(b.current_stock for b in m.batches)
        med_dict = {
            "id": m.id,
            "name": m.name,
            "generic_name": m.generic_name,
            "category": m.category,
            "unit": m.unit,
            "reorder_level": m.reorder_level,
            "total_stock": total_stock,
            "is_low_stock": total_stock <= m.reorder_level,
            "batches": m.batches,
            "created_at": m.created_at,
            "updated_at": m.updated_at,
        }
        med_list.append(med_dict)

    return med_list, total


async def stock_in(db: AsyncSession, req: StockInRequest) -> MedicineBatch:
    # Check if batch_no already exists for this medicine
    existing_res = await db.execute(
        select(MedicineBatch).where(
            MedicineBatch.medicine_id == req.medicine_id,
            MedicineBatch.batch_no == req.batch_no,
        )
    )
    batch = existing_res.scalar_one_or_none()

    if batch:
        batch.quantity_in += req.quantity
        batch.current_stock += req.quantity
        batch.unit_cost = req.unit_cost
        batch.supplier = req.supplier
        batch.expiry_date = req.expiry_date
    else:
        batch = MedicineBatch(
            medicine_id=req.medicine_id,
            batch_no=req.batch_no,
            expiry_date=req.expiry_date,
            quantity_in=req.quantity,
            quantity_out=0,
            current_stock=req.quantity,
            unit_cost=req.unit_cost,
            supplier=req.supplier,
        )
        db.add(batch)

    await db.flush()

    movement = StockMovement(
        medicine_id=req.medicine_id,
        batch_id=batch.id,
        movement_type="IN",
        quantity=req.quantity,
        reason=req.reason or "Purchase Stock In",
    )
    db.add(movement)
    await db.commit()
    await db.refresh(batch)
    return batch


async def stock_out(db: AsyncSession, req: StockOutRequest) -> int:
    remaining_to_dispense = req.quantity

    if req.batch_id:
        batch = (await db.execute(select(MedicineBatch).where(MedicineBatch.id == req.batch_id))).scalar_one_or_none()
        if not batch or batch.current_stock < req.quantity:
            raise ValueError(f"Insufficient stock in batch {req.batch_id}")
        batch.quantity_out += req.quantity
        batch.current_stock -= req.quantity
        db.add(batch)

        movement = StockMovement(
            medicine_id=req.medicine_id,
            batch_id=batch.id,
            movement_type="OUT",
            quantity=req.quantity,
            prescription_id=req.prescription_id,
            reason=req.reason or "Prescription Dispensed",
        )
        db.add(movement)
    else:
        # FIFO by earliest expiry date with positive stock
        batches_res = await db.execute(
            select(MedicineBatch)
            .where(
                MedicineBatch.medicine_id == req.medicine_id,
                MedicineBatch.current_stock > 0,
            )
            .order_by(MedicineBatch.expiry_date.asc())
        )
        batches = list(batches_res.scalars().all())
        total_available = sum(b.current_stock for b in batches)
        if total_available < req.quantity:
            raise ValueError(f"Insufficient stock. Available: {total_available}, Requested: {req.quantity}")

        for b in batches:
            if remaining_to_dispense <= 0:
                break
            take = min(b.current_stock, remaining_to_dispense)
            b.quantity_out += take
            b.current_stock -= take
            remaining_to_dispense -= take
            db.add(b)

            movement = StockMovement(
                medicine_id=req.medicine_id,
                batch_id=b.id,
                movement_type="OUT",
                quantity=take,
                prescription_id=req.prescription_id,
                reason=req.reason or "Prescription Dispensed",
            )
            db.add(movement)

    await db.commit()
    return req.quantity


async def get_low_stock_medicines(db: AsyncSession) -> List[dict]:
    result = await db.execute(
        select(Medicine).options(selectinload(Medicine.batches))
    )
    medicines = result.scalars().all()
    low_stock = []
    for m in medicines:
        stock = sum(b.current_stock for b in m.batches)
        if stock <= m.reorder_level:
            low_stock.append({
                "id": m.id,
                "name": m.name,
                "generic_name": m.generic_name,
                "unit": m.unit,
                "current_stock": stock,
                "reorder_level": m.reorder_level,
            })
    return low_stock


async def get_expiring_batches(db: AsyncSession, days: int = 30) -> List[dict]:
    cutoff = date.today() + timedelta(days=days)
    result = await db.execute(
        select(MedicineBatch)
        .options(selectinload(MedicineBatch.medicine))
        .where(
            MedicineBatch.current_stock > 0,
            MedicineBatch.expiry_date <= cutoff,
        )
        .order_by(MedicineBatch.expiry_date.asc())
    )
    batches = result.scalars().all()
    return [
        {
            "batch_id": b.id,
            "batch_no": b.batch_no,
            "medicine_name": b.medicine.name if b.medicine else "Unknown",
            "current_stock": b.current_stock,
            "expiry_date": str(b.expiry_date),
            "days_until_expiry": (b.expiry_date - date.today()).days,
        }
        for b in batches
    ]


async def get_inventory_valuation(db: AsyncSession) -> InventoryValuationOut:
    # Total medicines
    med_count_res = await db.execute(select(func.count(Medicine.id)))
    total_items_count = med_count_res.scalar_one()

    # Batches valuation
    batches_res = await db.execute(select(MedicineBatch).where(MedicineBatch.current_stock > 0))
    batches = list(batches_res.scalars().all())

    total_units = sum(b.current_stock for b in batches)
    total_val = sum(b.current_stock * b.unit_cost for b in batches)

    low_stock_items = await get_low_stock_medicines(db)
    expiring_soon = await get_expiring_batches(db, days=30)

    return InventoryValuationOut(
        total_items_count=total_items_count,
        total_units_in_stock=total_units,
        total_valuation_cost=round(total_val, 2),
        low_stock_medicines_count=len(low_stock_items),
        expiring_soon_count=len(expiring_soon),
    )
