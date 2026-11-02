import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_appointment_booking_conflict_and_completion(
    client: AsyncClient, admin_headers: dict, doctor_headers: dict
):
    # 1. Create Department
    dept_res = await client.post(
        "/api/v1/departments/",
        json={"name": "Dermatology", "description": "Skin Care", "floor": "2nd Floor"},
        headers=admin_headers,
    )
    assert dept_res.status_code == 201
    dept_id = dept_res.json()["id"]

    # 2. Create Doctor
    doc_res = await client.post(
        "/api/v1/doctors/",
        json={
            "full_name": "Dr. Dermatologist",
            "specialization": "Dermatology",
            "department_id": dept_id,
            "qualification": "MD - Harvard",
            "experience_years": 8,
            "phone": "+1 555-333-2222",
            "email": "derm.doc@hospital.com",
            "consultation_fee": 120.0,
            "available_days": ["Monday", "Tuesday", "Wednesday"],
            "working_hours_start": "09:00",
            "working_hours_end": "17:00",
        },
        headers=admin_headers,
    )
    assert doc_res.status_code == 201
    doctor_id = doc_res.json()["id"]

    # 3. Create Patient
    pat_res = await client.post(
        "/api/v1/patients/",
        json={
            "full_name": "Jane Eyre",
            "date_of_birth": "1994-02-10",
            "gender": "Female",
            "phone": "+1 555-999-1111",
            "email": "jane.eyre@example.com",
        },
        headers=admin_headers,
    )
    assert pat_res.status_code == 201
    patient_id = pat_res.json()["id"]

    # 4. Book appointment
    app_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_date": "2026-11-10",
        "time_slot": "10:00",
        "reason": "Skin rash evaluation",
        "is_recurring": False,
    }
    app_res = await client.post("/api/v1/appointments/", json=app_payload, headers=admin_headers)
    assert app_res.status_code == 201
    appointment = app_res.json()
    assert appointment["status"] == "scheduled"
    appointment_id = appointment["id"]

    # 5. Conflict Detection: booking same doctor at same date and slot must fail with 409
    conflict_res = await client.post("/api/v1/appointments/", json=app_payload, headers=admin_headers)
    assert conflict_res.status_code == 409
    assert "already booked" in conflict_res.json()["detail"].lower()

    # 6. Status Flow: update to confirmed, then in_progress
    conf_res = await client.patch(
        f"/api/v1/appointments/{appointment_id}",
        json={"status": "confirmed"},
        headers=admin_headers,
    )
    assert conf_res.status_code == 200
    assert conf_res.json()["status"] == "confirmed"

    # 7. Complete appointment with diagnosis and notes
    comp_res = await client.post(
        f"/api/v1/appointments/{appointment_id}/complete",
        json={
            "diagnosis": "Contact dermatitis due to synthetic fabric",
            "notes": "Prescribed topical corticosteroid ointment. Follow up in 10 days.",
        },
        headers=admin_headers,
    )
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["status"] == "completed"
    assert "Contact dermatitis" in comp_data["diagnosis"]
    assert "topical corticosteroid" in comp_data["notes"]
