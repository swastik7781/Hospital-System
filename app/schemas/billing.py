from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict
from app.models.billing import PaymentMethod, PaymentStatus
from app.schemas.patient import PatientOut


class InvoiceItemBase(BaseModel):
    description: str
    quantity: int = 1
    unit_price: float


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemOut(InvoiceItemBase):
    id: int
    invoice_id: int
    total_price: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceBase(BaseModel):
    patient_id: int
    discount: float = 0.0
    payment_method: PaymentMethod = PaymentMethod.CASH
    payment_status: PaymentStatus = PaymentStatus.PENDING
    amount_paid: float = 0.0
    provider_name: str | None = None
    policy_number: str | None = None
    claim_status: str | None = None


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]


class InvoiceUpdate(BaseModel):
    discount: float | None = None
    payment_method: PaymentMethod | None = None
    payment_status: PaymentStatus | None = None
    amount_paid: float | None = None
    provider_name: str | None = None
    policy_number: str | None = None
    claim_status: str | None = None


class InvoiceOut(InvoiceBase):
    id: int
    invoice_number: str
    subtotal: float
    tax: float
    total: float
    items: List[InvoiceItemOut] = []
    patient: PatientOut | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RevenueSummary(BaseModel):
    revenue_today: float
    revenue_this_week: float
    revenue_this_month: float
    total_revenue: float
    pending_payments_amount: float
    invoices_paid_count: int
    invoices_pending_count: int
