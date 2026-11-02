import enum
from datetime import date
from sqlalchemy import String, Date, Text, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Appointment(Base, TimestampMixin):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False)
    doctor_id: Mapped[int] = mapped_column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), index=True, nullable=False)
    appointment_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    time_slot: Mapped[str] = mapped_column(String(20), index=True, nullable=False)  # e.g., "09:00", "09:30"
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, index=True, nullable=False
    )
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurrence_pattern: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "weekly", "monthly"

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    prescription = relationship("Prescription", back_populates="visit", uselist=False)
