import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_patient_crud_and_soft_delete(
    client: AsyncClient, admin_headers: dict
):
    # 1. Register patient
    patient_payload = {
        "full_name": "Oliver Twist",
        "date_of_birth": "1996-05-15",
        "gender": "Male",
        "phone": "+1 555-777-8888",
        "email": "oliver.twist@example.com",
        "address": "48 Doughty St, London",
        "blood_group": "O+",
        "allergies": "Dust",
        "medical_history": "Childhood asthma",
        "emergency_contact": "+1 555-999-8888 (Mrs. Sowerberry)",
    }
    create_res = await client.post("/api/v1/patients/", json=patient_payload, headers=admin_headers)
    assert create_res.status_code == 201
    patient = create_res.json()
    patient_id = patient["id"]
    assert patient["full_name"] == "Oliver Twist"
    assert patient["is_deleted"] is False

    # 2. Get patient by id
    get_res = await client.get(f"/api/v1/patients/{patient_id}", headers=admin_headers)
    assert get_res.status_code == 200
    assert get_res.json()["phone"] == "+1 555-777-8888"

    # 3. Update patient
    update_res = await client.patch(
        f"/api/v1/patients/{patient_id}",
        json={"allergies": "Dust, Strawberries"},
        headers=admin_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["allergies"] == "Dust, Strawberries"

    # 4. Search patient in list
    search_res = await client.get("/api/v1/patients/?search=Oliver", headers=admin_headers)
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert any(p["id"] == patient_id for p in search_data["items"])

    # 5. Patient dashboard summary
    dash_res = await client.get(f"/api/v1/patients/{patient_id}/dashboard", headers=admin_headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["full_name"] == "Oliver Twist"
    assert "total_visits" in dash_data

    # 6. Soft delete
    del_res = await client.delete(f"/api/v1/patients/{patient_id}", headers=admin_headers)
    assert del_res.status_code == 200

    # 7. Verify soft deleted: querying directly returns 404 (or hidden from list)
    get_deleted = await client.get(f"/api/v1/patients/{patient_id}", headers=admin_headers)
    assert get_deleted.status_code == 404
