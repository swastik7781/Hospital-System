from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class PatientBase(BaseModel):
    full_name: str
    date_of_birth: date
    gender: str
    phone: str
    email: EmailStr | None = None
    address: str | None = None
    blood_group: str | None = None
    allergies: str | None = None
    medical_history: str | None = None
    emergency_contact: str | None = None


class PatientCreate(PatientBase):
    user_id: int | None = None


class PatientUpdate(BaseModel):
    full_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    blood_group: str | None = None
    allergies: str | None = None
    medical_history: str | None = None
    emergency_contact: str | None = None


class PatientOut(PatientBase):
    id: int
    user_id: int | None = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatientDashboardSummary(BaseModel):
    patient_id: int
    full_name: str
    total_visits: int
    active_prescriptions_count: int
    pending_reports_count: int
    unpaid_invoices_count: int
    upcoming_appointments: List[dict]
    recent_prescriptions: List[dict]
    recent_reports: List[dict]
