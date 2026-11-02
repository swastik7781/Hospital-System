import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_prescription_lifecycle_and_pdf(
    client: AsyncClient, admin_headers: dict
):
    # 1. Setup Patient and Doctor
    dept_res = await client.post(
        "/api/v1/departments/",
        json={"name": "Pulmonology", "description": "Lungs & Respiratory"},
        headers=admin_headers,
    )
    dept_id = dept_res.json()["id"]

    doc_res = await client.post(
        "/api/v1/doctors/",
        json={
            "full_name": "Dr. Lung Specialist",
            "specialization": "Pulmonology",
            "department_id": dept_id,
            "qualification": "MD - Johns Hopkins",
            "phone": "+1 555-888-1111",
            "email": "pulmo.doc@hospital.com",
            "consultation_fee": 140.0,
        },
        headers=admin_headers,
    )
    doctor_id = doc_res.json()["id"]

    pat_res = await client.post(
        "/api/v1/patients/",
        json={
            "full_name": "John Watson",
            "date_of_birth": "1980-07-07",
            "gender": "Male",
            "phone": "+1 555-222-3333",
            "email": "john.watson@example.com",
        },
        headers=admin_headers,
    )
    patient_id = pat_res.json()["id"]

    # 2. Create Prescription with multiple line items
    presc_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "instructions": "Inhale two puffs morning and evening. Avoid cold drinks.",
        "items": [
            {
                "medicine_name": "Albuterol Inhaler",
                "dosage": "100mcg",
                "frequency": "Twice daily",
                "duration": "30 days",
                "quantity": 1,
                "notes": "Rinse mouth after inhalation",
            },
            {
                "medicine_name": "Cetirizine 10mg",
                "dosage": "10mg",
                "frequency": "Once daily before sleep",
                "duration": "14 days",
                "quantity": 14,
                "notes": "For allergy symptoms",
            },
        ],
    }
    create_res = await client.post("/api/v1/prescriptions/", json=presc_payload, headers=admin_headers)
    assert create_res.status_code == 201
    presc_data = create_res.json()
    presc_id = presc_data["id"]
    assert len(presc_data["items"]) == 2
    assert presc_data["patient"]["full_name"] == "John Watson"

    # 3. Active prescriptions query
    active_res = await client.get(f"/api/v1/prescriptions/patient/{patient_id}/active", headers=admin_headers)
    assert active_res.status_code == 200
    active_list = active_res.json()
    assert len(active_list) >= 1
    assert any(p["id"] == presc_id for p in active_list)

    # 4. Generate and download printable PDF
    pdf_res = await client.get(f"/api/v1/prescriptions/{presc_id}/pdf", headers=admin_headers)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000  # valid PDF binary stream
    assert pdf_res.content.startswith(b"%PDF")
