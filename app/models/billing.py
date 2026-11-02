import enum
from sqlalchemy import String, Float, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    INSURANCE = "insurance"
    ONLINE = "online"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"


class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    discount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tax: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 5% default
    total: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    amount_paid: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), default=PaymentMethod.CASH, nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.PENDING, index=True, nullable=False
    )
    provider_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    policy_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    claim_status: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "submitted", "approved", "rejected"

    # Relationships
    patient = relationship("Patient", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base, TimestampMixin):
    __tablename__ = "invoice_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationship
    invoice = relationship("Invoice", back_populates="items")
