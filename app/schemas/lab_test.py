from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from app.models.lab_test import LabTestType, LabTestStatus
from app.schemas.doctor import DoctorOut
from app.schemas.patient import PatientOut


class LabTestBase(BaseModel):
    patient_id: int
    doctor_id: int
    test_type: LabTestType
    scheduled_date: date
    findings: str | None = None
    notes: str | None = None
    critical_value: bool = False


class LabTestCreate(LabTestBase):
    pass


class LabTestUpdate(BaseModel):
    test_type: LabTestType | None = None
    status: LabTestStatus | None = None
    scheduled_date: date | None = None
    findings: str | None = None
    notes: str | None = None
    critical_value: bool | None = None
    report_file: str | None = None


class LabTestOut(LabTestBase):
    id: int
    status: LabTestStatus
    report_file: str | None = None
    created_at: datetime
    updated_at: datetime
    patient: PatientOut | None = None
    doctor: DoctorOut | None = None

    model_config = ConfigDict(from_attributes=True)
