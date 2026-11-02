import uuid
from typing import Optional, List, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.billing import Invoice, InvoiceItem, PaymentMethod, PaymentStatus
from app.schemas.billing import InvoiceCreate, InvoiceUpdate, RevenueSummary


def generate_invoice_number() -> str:
    today_str = datetime.utcnow().strftime("%Y%m%d")
    unique_suffix = str(uuid.uuid4().hex[:6]).upper()
    return f"INV-{today_str}-{unique_suffix}"


async def get_invoice_by_id(db: AsyncSession, invoice_id: int) -> Optional[Invoice]:
    result = await db.execute(
        select(Invoice)
        .options(
            selectinload(Invoice.patient),
            selectinload(Invoice.items),
        )
        .where(Invoice.id == invoice_id)
    )
    return result.scalar_one_or_none()


async def get_invoice_by_number(db: AsyncSession, invoice_number: str) -> Optional[Invoice]:
    result = await db.execute(
        select(Invoice)
        .options(
            selectinload(Invoice.patient),
            selectinload(Invoice.items),
        )
        .where(Invoice.invoice_number == invoice_number)
    )
    return result.scalar_one_or_none()


async def create_invoice(db: AsyncSession, inv_in: InvoiceCreate) -> Invoice:
    # Auto-calculate subtotal
    subtotal = 0.0
    items_to_add = []
    for item in inv_in.items:
        line_total = round(item.quantity * item.unit_price, 2)
        subtotal += line_total
        items_to_add.append({
            "description": item.description,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": line_total,
        })

    discount = min(inv_in.discount, subtotal)
    taxable = max(0.0, subtotal - discount)
    tax = round(taxable * 0.05, 2)  # 5% tax
    total = round(taxable + tax, 2)

    # Determine status based on amount_paid
    status = inv_in.payment_status
    amount_paid = inv_in.amount_paid
    if amount_paid >= total and total > 0:
        status = PaymentStatus.PAID
    elif amount_paid > 0 and amount_paid < total:
        status = PaymentStatus.PARTIAL

    invoice = Invoice(
        invoice_number=generate_invoice_number(),
        patient_id=inv_in.patient_id,
        subtotal=subtotal,
        discount=discount,
        tax=tax,
        total=total,
        amount_paid=amount_paid,
        payment_method=inv_in.payment_method,
        payment_status=status,
        provider_name=inv_in.provider_name,
        policy_number=inv_in.policy_number,
        claim_status=inv_in.claim_status,
    )
    db.add(invoice)
    await db.flush()

    for item_data in items_to_add:
        invoice_item = InvoiceItem(invoice_id=invoice.id, **item_data)
        db.add(invoice_item)

    await db.commit()
    return await get_invoice_by_id(db, invoice.id)


async def update_invoice(db: AsyncSession, invoice: Invoice, inv_in: InvoiceUpdate) -> Invoice:
    update_data = inv_in.model_dump(exclude_unset=True)

    if "discount" in update_data:
        invoice.discount = min(update_data["discount"], invoice.subtotal)
        taxable = max(0.0, invoice.subtotal - invoice.discount)
        invoice.tax = round(taxable * 0.05, 2)
        invoice.total = round(taxable + invoice.tax, 2)

    if "amount_paid" in update_data:
        invoice.amount_paid = update_data["amount_paid"]
        if invoice.amount_paid >= invoice.total and invoice.total > 0:
            invoice.payment_status = PaymentStatus.PAID
        elif invoice.amount_paid > 0 and invoice.amount_paid < invoice.total:
            invoice.payment_status = PaymentStatus.PARTIAL
        elif invoice.amount_paid == 0:
            invoice.payment_status = PaymentStatus.PENDING

    for field, value in update_data.items():
        if field not in ("discount", "amount_paid"):
            setattr(invoice, field, value)

    db.add(invoice)
    await db.commit()
    return await get_invoice_by_id(db, invoice.id)


async def get_invoices_paginated(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    patient_id: Optional[int] = None,
    payment_status: Optional[PaymentStatus] = None,
    payment_method: Optional[PaymentMethod] = None,
) -> Tuple[List[Invoice], int]:
    query = select(Invoice).options(
        selectinload(Invoice.patient),
        selectinload(Invoice.items),
    )

    if patient_id is not None:
        query = query.where(Invoice.patient_id == patient_id)
    if payment_status is not None:
        query = query.where(Invoice.payment_status == payment_status)
    if payment_method is not None:
        query = query.where(Invoice.payment_method == payment_method)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    offset = (page - 1) * page_size
    query = query.order_by(Invoice.id.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_revenue_summary(db: AsyncSession) -> RevenueSummary:
    now = datetime.utcnow()
    start_today = datetime(now.year, now.month, now.day)
    start_week = start_today - timedelta(days=now.weekday())
    start_month = datetime(now.year, now.month, 1)

    # Today revenue
    today_res = await db.execute(
        select(func.sum(Invoice.amount_paid)).where(Invoice.created_at >= start_today)
    )
    rev_today = float(today_res.scalar_one() or 0.0)

    # This week revenue
    week_res = await db.execute(
        select(func.sum(Invoice.amount_paid)).where(Invoice.created_at >= start_week)
    )
    rev_week = float(week_res.scalar_one() or 0.0)

    # This month revenue
    month_res = await db.execute(
        select(func.sum(Invoice.amount_paid)).where(Invoice.created_at >= start_month)
    )
    rev_month = float(month_res.scalar_one() or 0.0)

    # Total revenue
    total_res = await db.execute(select(func.sum(Invoice.amount_paid)))
    rev_total = float(total_res.scalar_one() or 0.0)

    # Pending amount
    pending_res = await db.execute(
        select(func.sum(Invoice.total - Invoice.amount_paid)).where(
            Invoice.payment_status != PaymentStatus.PAID
        )
    )
    pending_amount = float(pending_res.scalar_one() or 0.0)

    # Counts
    paid_count_res = await db.execute(
        select(func.count(Invoice.id)).where(Invoice.payment_status == PaymentStatus.PAID)
    )
    invoices_paid_count = paid_count_res.scalar_one()

    pending_count_res = await db.execute(
        select(func.count(Invoice.id)).where(Invoice.payment_status != PaymentStatus.PAID)
    )
    invoices_pending_count = pending_count_res.scalar_one()

    return RevenueSummary(
        revenue_today=rev_today,
        revenue_this_week=rev_week,
        revenue_this_month=rev_month,
        total_revenue=rev_total,
        pending_payments_amount=pending_amount,
        invoices_paid_count=invoices_paid_count,
        invoices_pending_count=invoices_pending_count,
    )
