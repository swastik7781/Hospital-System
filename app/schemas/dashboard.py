from typing import List, Any
from pydantic import BaseModel


class DashboardKPIs(BaseModel):
    total_patients: int
    today_appointments: int
    revenue_today: float
    revenue_this_month: float
    active_prescriptions: int
    low_stock_count: int
    pending_reports: int


class ChartDataPoint(BaseModel):
    label: str
    value: float | int
    secondary_value: float | int | None = None


class ActivityItem(BaseModel):
    id: str
    type: str  # "appointment", "prescription", "lab_test", "billing", "patient"
    title: str
    description: str
    timestamp: str
    badge_color: str


class AlertItem(BaseModel):
    id: str
    category: str  # "critical_lab", "expiring_medicine", "no_show"
    title: str
    message: str
    severity: str  # "error", "warning", "info"
    created_at: str


class AdminDashboardResponse(BaseModel):
    kpis: DashboardKPIs
    appointments_by_day: List[ChartDataPoint]
    revenue_trend: List[ChartDataPoint]
    visits_by_department: List[ChartDataPoint]
    top_doctors: List[ChartDataPoint]
    recent_activity: List[ActivityItem]
    alerts: List[AlertItem]
