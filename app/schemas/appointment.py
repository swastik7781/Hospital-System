from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from app.models.appointment import AppointmentStatus
from app.schemas.doctor import DoctorOut
from app.schemas.patient import PatientOut


class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    time_slot: str  # e.g., "09:00", "09:30"
    reason: str
    is_recurring: bool = False
    recurrence_pattern: str | None = None  # "weekly", "monthly"


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    appointment_date: date | None = None
    time_slot: str | None = None
    reason: str | None = None
    status: AppointmentStatus | None = None
    diagnosis: str | None = None
    notes: str | None = None
    is_recurring: bool | None = None
    recurrence_pattern: str | None = None


class AppointmentComplete(BaseModel):
    diagnosis: str
    notes: str | None = None


class AppointmentOut(AppointmentBase):
    id: int
    status: AppointmentStatus
    diagnosis: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    patient: PatientOut | None = None
    doctor: DoctorOut | None = None

    model_config = ConfigDict(from_attributes=True)
