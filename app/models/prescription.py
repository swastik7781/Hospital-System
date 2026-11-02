from datetime import date
from sqlalchemy import String, Date, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class Prescription(Base, TimestampMixin):
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    visit_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False)
    doctor_id: Mapped[int] = mapped_column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), index=True, nullable=False)
    prescription_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    visit = relationship("Appointment", back_populates="prescription")
    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("Doctor", back_populates="prescriptions")
    items = relationship("PrescriptionItem", back_populates="prescription", cascade="all, delete-orphan")


class PrescriptionItem(Base, TimestampMixin):
    __tablename__ = "prescription_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    prescription_id: Mapped[int] = mapped_column(Integer, ForeignKey("prescriptions.id", ondelete="CASCADE"), nullable=False)
    medicine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[str] = mapped_column(String(100), nullable=False)       # e.g. "500mg"
    frequency: Mapped[str] = mapped_column(String(100), nullable=False)    # e.g. "Twice a day after meals"
    duration: Mapped[str] = mapped_column(String(100), nullable=False)     # e.g. "5 days"
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationship
    prescription = relationship("Prescription", back_populates="items")
