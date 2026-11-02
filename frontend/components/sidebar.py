import reflex as rx


def sidebar_item(label: str, icon_name: str, route_path: str, is_active: bool = False) -> rx.Component:
    active_style = {
        "background": "#F0FDFA",
        "color": "#0D9488",
        "font_weight": "600",
        "border_left": "3px solid #0D9488",
    } if is_active else {
        "color": "#475569",
        "font_weight": "500",
        "border_left": "3px solid transparent",
    }

    return rx.link(
        rx.hstack(
            rx.icon(icon_name, size=18),
            rx.text(label, font_size="14px"),
            spacing="3",
            align_items="center",
            padding="10px 16px",
            border_radius="6px",
            transition="all 0.15s ease",
            _hover={
                "background": "#F8FAFC",
                "color": "#0D9488",
            },
            **active_style,
        ),
        href=route_path,
        text_decoration="none",
        width="100%",
    )


def sidebar(current_page: str = "dashboard", user_role: str = "admin") -> rx.Component:
    admin_doctor_recept = ["admin", "doctor", "receptionist"]

    return rx.box(
        rx.vstack(
            # Header Branding
            rx.hstack(
                rx.box(
                    rx.text("🏥", font_size="20px"),
                    background="#CCFBF1",
                    padding="6px 10px",
                    border_radius="10px",
                ),
                rx.vstack(
                    rx.text("Utkal Hospital", font_weight="700", font_size="16px", color="#0F172A"),
                    rx.text("Clinical Health Suite", font_size="11px", color="#64748B"),
                    spacing="0",
                ),
                align_items="center",
                padding="20px 16px 24px 16px",
                border_bottom="1px solid #F1F5F9",
                width="100%",
            ),

            # Navigation Links
            rx.vstack(
                sidebar_item("Dashboard", "layout-dashboard", "/dashboard", current_page == "dashboard"),
                sidebar_item("Patients", "users", "/patients", current_page == "patients"),
                sidebar_item("Appointments", "calendar", "/appointments", current_page == "appointments"),
                rx.cond(
                    user_role in admin_doctor_recept,
                    sidebar_item("Doctors", "stethoscope", "/doctors", current_page == "doctors"),
                ),
                sidebar_item("Prescriptions", "pill", "/prescriptions", current_page == "prescriptions"),
                sidebar_item("Lab Reports", "flask-conical", "/lab-reports", current_page == "lab_reports"),
                rx.cond(
                    user_role in ["admin", "receptionist"],
                    sidebar_item("Billing & Invoices", "credit-card", "/billing", current_page == "billing"),
                ),
                rx.cond(
                    user_role in ["admin", "doctor", "receptionist"],
                    sidebar_item("Pharmacy", "package", "/pharmacy", current_page == "pharmacy"),
                ),
                sidebar_item("Settings", "settings", "/settings", current_page == "settings"),
                spacing="1",
                width="100%",
                padding="16px 12px",
            ),
            width="100%",
        ),
        width="260px",
        height="100vh",
        background="#FFFFFF",
        border_right="1px solid #E2E8F0",
        position="sticky",
        top="0",
    )
