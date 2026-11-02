import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_roles(
    client: AsyncClient,
    admin_headers: dict,
    doctor_headers: dict,
    patient_headers: dict,
):
    # 1. Admin Dashboard View
    admin_dash = await client.get("/api/v1/dashboard/admin", headers=admin_headers)
    assert admin_dash.status_code == 200
    data = admin_dash.json()
    assert "kpis" in data
    assert "appointments_by_day" in data
    assert "recent_activity" in data

    # 2. Doctor Dashboard View
    doc_dash = await client.get("/api/v1/dashboard/admin", headers=doctor_headers)
    assert doc_dash.status_code == 200
    doc_data = doc_dash.json()
    assert "kpis" in doc_data
    assert "alerts" in doc_data

    # 3. Patient Dashboard View
    pat_dash = await client.get("/api/v1/dashboard/admin", headers=patient_headers)
    assert pat_dash.status_code == 200
    pat_data = pat_dash.json()
    assert "kpis" in pat_data

