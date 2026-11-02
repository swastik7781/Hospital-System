import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_billing_calculations_payments_and_revenue(
    client: AsyncClient, admin_headers: dict
):
    # 1. Create Patient
    pat_res = await client.post(
        "/api/v1/patients/",
        json={
            "full_name": "Ebenezer Scrooge",
            "date_of_birth": "1960-12-25",
            "gender": "Male",
            "phone": "+1 555-000-1111",
            "email": "scrooge@example.com",
        },
        headers=admin_headers,
    )
    assert pat_res.status_code == 201
    patient_id = pat_res.json()["id"]

    # 2. Create Invoice: subtotal = (2 * 50) + (1 * 100) = 200. Discount = 20. Taxable = 180. Tax 5% = 9. Total = 189.
    inv_payload = {
        "patient_id": patient_id,
        "discount": 20.0,
        "payment_method": "card",
        "payment_status": "pending",
        "amount_paid": 0.0,
        "items": [
            {"description": "Blood Sugar Clinical Test", "quantity": 2, "unit_price": 50.0},
            {"description": "ECG Interpretation", "quantity": 1, "unit_price": 100.0},
        ],
    }
    create_res = await client.post("/api/v1/billing/invoices", json=inv_payload, headers=admin_headers)
    assert create_res.status_code == 201
    inv_data = create_res.json()
    inv_id = inv_data["id"]

    assert inv_data["subtotal"] == 200.0
    assert inv_data["discount"] == 20.0
    assert inv_data["tax"] == 9.0
    assert inv_data["total"] == 189.0
    assert inv_data["payment_status"] == "pending"

    # 3. Partial payment
    partial_res = await client.patch(
        f"/api/v1/billing/invoices/{inv_id}",
        json={"amount_paid": 100.0},
        headers=admin_headers,
    )
    assert partial_res.status_code == 200
    assert partial_res.json()["payment_status"] == "partial"
    assert partial_res.json()["amount_paid"] == 100.0

    # 4. Full payment
    full_res = await client.patch(
        f"/api/v1/billing/invoices/{inv_id}",
        json={"amount_paid": 189.0},
        headers=admin_headers,
    )
    assert full_res.status_code == 200
    assert full_res.json()["payment_status"] == "paid"

    # 5. Revenue summary
    rev_res = await client.get("/api/v1/billing/revenue-summary", headers=admin_headers)
    assert rev_res.status_code == 200
    rev_data = rev_res.json()
    assert rev_data["total_revenue"] >= 189.0
    assert rev_data["invoices_paid_count"] >= 1
