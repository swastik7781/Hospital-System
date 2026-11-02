from sqlalchemy import String, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class Doctor(Base, TimestampMixin):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    specialization: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    qualification: Mapped[str] = mapped_column(String(255), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    consultation_fee: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    available_days: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    working_hours_start: Mapped[str] = mapped_column(String(10), default="09:00", nullable=False)
    working_hours_end: Mapped[str] = mapped_column(String(10), default="17:00", nullable=False)

    # Relationships
    department = relationship("Department", foreign_keys=[department_id], back_populates="doctors")
    user = relationship("User", foreign_keys=[user_id])
    appointments = relationship("Appointment", back_populates="doctor")
    prescriptions = relationship("Prescription", back_populates="doctor")
