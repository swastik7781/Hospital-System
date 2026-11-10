from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict, computed_field


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
    password: Optional[str] = None
    create_portal_account: bool = True


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
    has_portal_account: bool = False
    portal_username: Optional[str] = None

    @computed_field
    @property
    def mrn(self) -> str:
        return f"UTK-{1000 + self.id}"

    model_config = ConfigDict(from_attributes=True)


class PatientPortalAccountCreate(BaseModel):
    password: Optional[str] = "patient123"
    email: Optional[EmailStr] = None


class PatientPortalAccountDirectoryItem(BaseModel):
    patient_id: int
    mrn: str
    full_name: str
    email: Optional[str] = None
    phone: str
    gender: str
    blood_group: Optional[str] = None
    has_portal_account: bool
    default_password: str = "patient123"


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
