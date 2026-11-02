from datetime import date, datetime
from typing import List
from pydantic import BaseModel, ConfigDict


class MedicineBase(BaseModel):
    name: str
    generic_name: str
    category: str
    unit: str  # tablet, capsule, bottle, vial, etc.
    reorder_level: int = 50


class MedicineCreate(MedicineBase):
    pass


class MedicineUpdate(BaseModel):
    name: str | None = None
    generic_name: str | None = None
    category: str | None = None
    unit: str | None = None
    reorder_level: int | None = None


class MedicineBatchBase(BaseModel):
    batch_no: str
    expiry_date: date
    quantity_in: int
    unit_cost: float
    supplier: str


class MedicineBatchCreate(MedicineBatchBase):
    medicine_id: int


class MedicineBatchOut(MedicineBatchBase):
    id: int
    medicine_id: int
    quantity_out: int
    current_stock: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicineOut(MedicineBase):
    id: int
    total_stock: int = 0
    is_low_stock: bool = False
    batches: List[MedicineBatchOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockInRequest(BaseModel):
    medicine_id: int
    batch_no: str
    expiry_date: date
    quantity: int
    unit_cost: float
    supplier: str
    reason: str | None = "Purchase"


class StockOutRequest(BaseModel):
    medicine_id: int
    batch_id: int | None = None
    quantity: int
    prescription_id: int | None = None
    reason: str | None = "Dispensed"


class InventoryValuationOut(BaseModel):
    total_items_count: int
    total_units_in_stock: int
    total_valuation_cost: float
    low_stock_medicines_count: int
    expiring_soon_count: int
