from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.departments import router as departments_router
from app.routers.doctors import router as doctors_router
from app.routers.patients import router as patients_router
from app.routers.appointments import router as appointments_router
from app.routers.prescriptions import router as prescriptions_router
from app.routers.lab_tests import router as lab_tests_router
from app.routers.billing import router as billing_router
from app.routers.pharmacy import router as pharmacy_router
from app.routers.dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "users_router",
    "departments_router",
    "doctors_router",
    "patients_router",
    "appointments_router",
    "prescriptions_router",
    "lab_tests_router",
    "billing_router",
    "pharmacy_router",
    "dashboard_router",
]
