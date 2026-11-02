from datetime import datetime
from typing import List
from pydantic import BaseModel, EmailStr, ConfigDict
from app.schemas.department import DepartmentOut


class DoctorBase(BaseModel):
    full_name: str
    specialization: str
    department_id: int
    qualification: str
    experience_years: int = 0
    phone: str
    email: EmailStr
    consultation_fee: float = 0.0
    available_days: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    working_hours_start: str = "09:00"
    working_hours_end: str = "17:00"
    user_id: int | None = None


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    full_name: str | None = None
    specialization: str | None = None
    department_id: int | None = None
    qualification: str | None = None
    experience_years: int | None = None
    phone: str | None = None
    email: EmailStr | None = None
    consultation_fee: float | None = None
    available_days: List[str] | None = None
    working_hours_start: str | None = None
    working_hours_end: str | None = None
    user_id: int | None = None


class DoctorOut(DoctorBase):
    id: int
    department: DepartmentOut | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DoctorScheduleOut(BaseModel):
    doctor_id: int
    doctor_name: str
    specialization: str
    department_name: str
    available_days: List[str]
    working_hours_start: str
    working_hours_end: str
    time_slots: List[str]
