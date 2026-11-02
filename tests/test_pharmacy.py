from datetime import date, timedelta
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_pharmacy_inventory_lifecycle(
    client: AsyncClient, admin_headers: dict
):
    # 1. Create Medicine
    med_payload = {
        "name": "Azithromycin 250mg",
        "generic_name": "Azithromycin",
        "category": "Antibiotic",
        "unit": "tablet",
        "reorder_level": 50,
    }
    create_res = await client.post("/api/v1/pharmacy/medicines", json=med_payload, headers=admin_headers)
    assert create_res.status_code == 201
    med = create_res.json()
    med_id = med["id"]
    assert med["is_low_stock"] is True
    assert med["total_stock"] == 0

    # 2. Stock In (Purchase 100 tablets in Batch A)
    today = date.today()
    stock_in_payload = {
        "medicine_id": med_id,
        "batch_no": "AZI-BATCH-001",
        "expiry_date": str(today + timedelta(days=20)),  # Expiring soon (<30 days)
        "quantity": 100,
        "unit_cost": 1.50,
        "supplier": "Apex Pharma",
        "reason": "Initial Purchase",
    }
    stock_in_res = await client.post("/api/v1/pharmacy/stock-in", json=stock_in_payload, headers=admin_headers)
    assert stock_in_res.status_code == 200
    batch_data = stock_in_res.json()
    assert batch_data["current_stock"] == 100

    # Check medicine now reflects total stock = 100 (not low stock since 100 > 50)
    med_res = await client.get(f"/api/v1/pharmacy/medicines/{med_id}", headers=admin_headers)
    assert med_res.status_code == 200
    assert med_res.json()["total_stock"] == 100
    assert med_res.json()["is_low_stock"] is False

    # 3. Stock Out (Dispense 60 tablets -> remaining 40 <= reorder_level 50 -> low stock alert triggered!)
    stock_out_payload = {
        "medicine_id": med_id,
        "quantity": 60,
        "reason": "Prescription Dispense",
    }
    dispense_res = await client.post("/api/v1/pharmacy/stock-out", json=stock_out_payload, headers=admin_headers)
    assert dispense_res.status_code == 200

    # Verify updated stock
    med_after = await client.get(f"/api/v1/pharmacy/medicines/{med_id}", headers=admin_headers)
    assert med_after.json()["total_stock"] == 40
    assert med_after.json()["is_low_stock"] is True

    # 4. Low stock alert endpoint check
    low_stock_res = await client.get("/api/v1/pharmacy/alerts/low-stock", headers=admin_headers)
    assert low_stock_res.status_code == 200
    low_stock_list = low_stock_res.json()
    assert any(m["id"] == med_id for m in low_stock_list)

    # 5. Expiring batches alert endpoint check (within 30 days)
    expiring_res = await client.get("/api/v1/pharmacy/alerts/expiring?days=30", headers=admin_headers)
    assert expiring_res.status_code == 200
    exp_list = expiring_res.json()
    assert any(b["batch_no"] == "AZI-BATCH-001" for b in exp_list)

    # 6. Inventory valuation
    val_res = await client.get("/api/v1/pharmacy/valuation", headers=admin_headers)
    assert val_res.status_code == 200
    valuation = val_res.json()
    assert valuation["total_items_count"] >= 1
    assert valuation["total_units_in_stock"] >= 40
    assert valuation["total_valuation_cost"] >= 60.0  # 40 * 1.50 = 60.0
