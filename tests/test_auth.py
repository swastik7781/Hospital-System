import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # Register new user
    register_payload = {
        "email": "newuser@hospital.com",
        "password": "securepassword123",
        "full_name": "New Registered User",
        "role": "patient",
        "phone": "+1 555-444-3333",
    }
    res = await client.post("/api/v1/auth/register", json=register_payload)
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "newuser@hospital.com"
    assert data["role"] == "patient"

    # Duplicate registration should fail with 409
    res_dup = await client.post("/api/v1/auth/register", json=register_payload)
    assert res_dup.status_code == 409

    # Login
    login_payload = {
        "email": "newuser@hospital.com",
        "password": "securepassword123",
    }
    res_login = await client.post("/api/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    token_data = res_login.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Refresh token
    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token_data["refresh_token"]},
    )
    assert refresh_res.status_code == 200
    refreshed_data = refresh_res.json()
    assert "access_token" in refreshed_data

    # Profile check with Bearer token
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_res = await client.get("/api/v1/users/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "newuser@hospital.com"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@hospital.com", "password": "wrongpassword"},
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_role_based_access_control(
    client: AsyncClient, patient_headers: dict, admin_headers: dict
):
    # Patient attempting admin user list route -> 403 Forbidden
    res_patient = await client.get("/api/v1/users/", headers=patient_headers)
    assert res_patient.status_code == 403

    # Admin attempting admin user list route -> 200 OK
    res_admin = await client.get("/api/v1/users/", headers=admin_headers)
    assert res_admin.status_code == 200
    assert "items" in res_admin.json()
