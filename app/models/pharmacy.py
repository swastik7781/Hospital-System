from datetime import date
from sqlalchemy import String, Date, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class Medicine(Base, TimestampMixin):
    __tablename__ = "medicines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    generic_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)  # tablet, capsule, syrup, injection
    reorder_level: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    # Relationships
    batches = relationship("MedicineBatch", back_populates="medicine", cascade="all, delete-orphan")
    movements = relationship("StockMovement", back_populates="medicine")


class MedicineBatch(Base, TimestampMixin):
    __tablename__ = "medicine_batches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    medicine_id: Mapped[int] = mapped_column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), index=True, nullable=False)
    batch_no: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    quantity_in: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quantity_out: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    supplier: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    medicine = relationship("Medicine", back_populates="batches")
    movements = relationship("StockMovement", back_populates="batch")


class StockMovement(Base, TimestampMixin):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    medicine_id: Mapped[int] = mapped_column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    batch_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("medicine_batches.id", ondelete="SET NULL"), nullable=True)
    movement_type: Mapped[str] = mapped_column(String(10), nullable=False)  # "IN" or "OUT"
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    prescription_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("prescriptions.id", ondelete="SET NULL"), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    medicine = relationship("Medicine", back_populates="movements")
    batch = relationship("MedicineBatch", back_populates="movements")
