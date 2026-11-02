from datetime import date, datetime
from typing import List
from pydantic import BaseModel, ConfigDict
from app.schemas.doctor import DoctorOut
from app.schemas.patient import PatientOut


class PrescriptionItemBase(BaseModel):
    medicine_name: str
    dosage: str
    frequency: str
    duration: str
    quantity: int = 1
    notes: str | None = None


class PrescriptionItemCreate(PrescriptionItemBase):
    pass


class PrescriptionItemOut(PrescriptionItemBase):
    id: int
    prescription_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PrescriptionBase(BaseModel):
    visit_id: int | None = None
    patient_id: int
    doctor_id: int
    prescription_date: date = date.today()
    instructions: str | None = None


class PrescriptionCreate(PrescriptionBase):
    items: List[PrescriptionItemCreate] = []


class PrescriptionUpdate(BaseModel):
    instructions: str | None = None
    items: List[PrescriptionItemCreate] | None = None


class PrescriptionOut(PrescriptionBase):
    id: int
    items: List[PrescriptionItemOut] = []
    patient: PatientOut | None = None
    doctor: DoctorOut | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
