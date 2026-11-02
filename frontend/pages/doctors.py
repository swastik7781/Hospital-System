import reflex as rx
from frontend.state import State
from frontend.components.sidebar import sidebar
from frontend.components.navbar import navbar
from frontend.components.animated_card import animated_card


def doctor_card(name: str, spec: str, dept: str, qual: str, exp: int, fee: float, phone: str, email: str) -> rx.Component:
    return animated_card(
        rx.vstack(
            rx.hstack(
                rx.avatar(name=name, size="3", background="#0D9488"),
                rx.vstack(
                    rx.text(name, font_weight="700", font_size="15px", color="#0F172A"),
                    rx.text(spec, font_size="13px", color="#0D9488", font_weight="600"),
                    rx.text(f"Department: {dept}", font_size="11px", color="#64748B"),
                    spacing="0",
                    align_items="flex-start",
                ),
                spacing="3",
                align_items="center",
            ),
            rx.divider(margin_y="12px"),
            rx.vstack(
                rx.hstack(
                    rx.text("Qualification:", font_size="12px", color="#64748B"),
                    rx.text(qual, font_size="12px", font_weight="600", color="#1E293B"),
                ),
                rx.hstack(
                    rx.text("Experience:", font_size="12px", color="#64748B"),
                    rx.text(f"{exp} Years", font_size="12px", font_weight="600", color="#1E293B"),
                ),
                rx.hstack(
                    rx.text("Consultation Fee:", font_size="12px", color="#64748B"),
                    rx.text(f"${fee:.2f}", font_size="12px", font_weight="700", color="#10B981"),
                ),
                rx.hstack(
                    rx.text("Contact:", font_size="12px", color="#64748B"),
                    rx.text(phone, font_size="12px", font_weight="500", color="#1E293B"),
                ),
                spacing="1",
                align_items="flex-start",
                width="100%",
            ),
            rx.button(
                "View Schedule Grid",
                variant="outline",
                color_scheme="teal",
                width="100%",
                margin_top="12px",
                size="1",
            ),
            align_items="flex-start",
            width="100%",
        ),
        width="100%",
    )


def doctors_page() -> rx.Component:
    return rx.hstack(
        sidebar(current_page="doctors", user_role=State.user_role),
        rx.vstack(
            navbar(user_name=State.user_name, user_role=State.user_role),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.text("Medical Specialists & Doctors", font_size="22px", font_weight="700", color="#0F172A"),
                            rx.text("Explore departmental faculty, qualifications, and weekly consultation schedules", font_size="13px", color="#64748B"),
                            align_items="flex-start",
                            spacing="0",
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.icon("user-plus", size=16),
                            "Add Doctor",
                            background="#0D9488",
                            color="white",
                            border_radius="8px",
                            padding="8px 18px",
                        ),
                        width="100%",
                        align_items="center",
                        margin_bottom="24px",
                    ),
                    rx.grid(
                        doctor_card("Dr. Alexander Wright", "Cardiology", "Cardiology", "MD, FACC - Harvard", 16, 150.0, "+1 555-020-0001", "alexander.wright@hospital.com"),
                        doctor_card("Dr. Maria Rodriguez", "Cardiology", "Cardiology", "MD - Johns Hopkins", 12, 160.0, "+1 555-020-0002", "maria.rodriguez@hospital.com"),
                        doctor_card("Dr. Robert Chen", "Neurology", "Neurology", "MD, PhD - Stanford", 14, 180.0, "+1 555-020-0003", "robert.chen@hospital.com"),
                        doctor_card("Dr. Emily Watson", "Neurology", "Neurology", "MBBS, MD - Oxford", 9, 170.0, "+1 555-020-0004", "emily.watson@hospital.com"),
                        doctor_card("Dr. David Kim", "Pediatrics", "Pediatrics", "MD - Boston Children's", 11, 120.0, "+1 555-020-0005", "david.kim@hospital.com"),
                        doctor_card("Dr. Michael Chang", "Orthopedics", "Orthopedics", "MD - Mayo Clinic", 15, 160.0, "+1 555-020-0007", "michael.chang@hospital.com"),
                        columns="3",
                        spacing="4",
                        width="100%",
                    ),
                    width="100%",
                ),
                padding="32px",
                width="100%",
            ),
            width="calc(100vw - 260px)",
            spacing="0",
            background="#F8FAFC",
            min_height="100vh",
        ),
        spacing="0",
        width="100%",
    )
