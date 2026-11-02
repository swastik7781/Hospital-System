import reflex as rx
from frontend.pages import (
    login_page,
    dashboard_page,
    patients_page,
    patient_detail_page,
    doctors_page,
    appointments_page,
    prescriptions_page,
    lab_reports_page,
    billing_page,
    pharmacy_page,
    settings_page,
)

style = {
    "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "background_color": "#F8FAFC",
}

app = rx.App(style=style)

# Add routes
app.add_page(login_page, route="/login", title="Login | Utkal Hospital")
app.add_page(dashboard_page, route="/", title="Dashboard | Utkal Hospital")
app.add_page(dashboard_page, route="/dashboard", title="Dashboard | Utkal Hospital")
app.add_page(patients_page, route="/patients", title="Patients Directory | Utkal Hospital")
app.add_page(patient_detail_page, route="/patients/[patient_id]", title="Patient Chart | Utkal Hospital")
app.add_page(doctors_page, route="/doctors", title="Doctors Faculty | Utkal Hospital")
app.add_page(appointments_page, route="/appointments", title="Appointments | Utkal Hospital")
app.add_page(prescriptions_page, route="/prescriptions", title="Prescriptions | Utkal Hospital")
app.add_page(lab_reports_page, route="/lab-reports", title="Lab Reports | Utkal Hospital")
app.add_page(billing_page, route="/billing", title="Billing & Invoices | Utkal Hospital")
app.add_page(pharmacy_page, route="/pharmacy", title="Pharmacy Dispensary | Utkal Hospital")
app.add_page(settings_page, route="/settings", title="Settings | Utkal Hospital")
