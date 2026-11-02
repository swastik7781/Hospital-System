import enum
from datetime import date
from sqlalchemy import String, Date, Text, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class LabTestType(str, enum.Enum):
    BLOOD_WORK = "blood_work"
    XRAY = "xray"
    MRI = "mri"
    CT_SCAN = "ct_scan"
    ULTRASOUND = "ultrasound"
    BIOPSY = "biopsy"
    OTHER = "other"


class LabTestStatus(str, enum.Enum):
    ORDERED = "ordered"
    SAMPLE_COLLECTED = "sample_collected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class LabTest(Base, TimestampMixin):
    __tablename__ = "lab_tests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False)
    doctor_id: Mapped[int] = mapped_column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), index=True, nullable=False)
    test_type: Mapped[LabTestType] = mapped_column(Enum(LabTestType), nullable=False)
    status: Mapped[LabTestStatus] = mapped_column(
        Enum(LabTestStatus), default=LabTestStatus.ORDERED, index=True, nullable=False
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    report_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    findings: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    critical_value: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="lab_tests")
    doctor = relationship("Doctor")
