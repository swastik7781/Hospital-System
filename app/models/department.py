from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class Department(Base, TimestampMixin):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    floor: Mapped[str | None] = mapped_column(String(50), nullable=True)
    head_doctor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("doctors.id", ondelete="SET NULL", use_alter=True), nullable=True)

    # Relationships
    doctors = relationship("Doctor", foreign_keys="Doctor.department_id", back_populates="department")
