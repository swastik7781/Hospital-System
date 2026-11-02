import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_lab_test_lifecycle(client: AsyncClient, admin_headers: dict):
    # 1. Create Department, Doctor, Patient
    dept_res = await client.post(
        "/api/v1/departments/",
        json={"name": "Pathology & Imaging", "description": "Diagnostics Center"},
        headers=admin_headers,
    )
    dept_id = dept_res.json()["id"]

    doc_res = await client.post(
        "/api/v1/doctors/",
        json={
            "full_name": "Dr. Radiologist",
            "specialization": "Radiology",
            "department_id": dept_id,
            "qualification": "MD - Radio-Diagnosis",
            "phone": "+91 98610 99999",
            "email": "radiology@utkalhospital.com",
            "consultation_fee": 1000.0,
        },
        headers=admin_headers,
    )
    doctor_id = doc_res.json()["id"]

    pat_res = await client.post(
        "/api/v1/patients/",
        json={
            "full_name": "Siddharth Mohanty",
            "date_of_birth": "1988-05-15",
            "gender": "Male",
            "phone": "+91 94370 88888",
            "email": "siddharth@example.com",
        },
        headers=admin_headers,
    )
    patient_id = pat_res.json()["id"]

    # 2. Order Lab Test
    order_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "test_type": "mri",
        "scheduled_date": "2026-11-12",
        "notes": "Persistent lower back pain radiating to left leg",
        "critical_value": False,
    }
    create_res = await client.post("/api/v1/lab-tests/", json=order_payload, headers=admin_headers)
    assert create_res.status_code == 201
    lab_data = create_res.json()
    assert lab_data["test_type"] == "mri"
    assert lab_data["status"] == "ordered"
    lab_id = lab_data["id"]

    # 3. Update Lab Test Findings & Mark Complete with Critical Flag
    update_res = await client.patch(
        f"/api/v1/lab-tests/{lab_id}",
        json={
            "status": "completed",
            "findings": "L4-L5 disc extrusion causing significant nerve root compression.",
            "critical_value": True,
        },
        headers=admin_headers,
    )
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["status"] == "completed"
    assert updated_data["critical_value"] is True
    assert "L4-L5 disc extrusion" in updated_data["findings"]

    # 4. Filter Lab Tests
    filter_res = await client.get("/api/v1/lab-tests/?critical_only=true", headers=admin_headers)
    assert filter_res.status_code == 200
    critical_items = filter_res.json()["items"]
    assert any(t["id"] == lab_id for t in critical_items)
