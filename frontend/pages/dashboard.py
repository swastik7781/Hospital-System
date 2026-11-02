import reflex as rx
from frontend.state import State
from frontend.components.sidebar import sidebar
from frontend.components.navbar import navbar
from frontend.components.animated_card import animated_card
from frontend.components.status_badge import status_badge


def kpi_card(title: str, value: str, subtext: str, icon_name: str, color_hex: str) -> rx.Component:
    return animated_card(
        rx.hstack(
            rx.vstack(
                rx.text(title, font_size="13px", font_weight="500", color="#64748B"),
                rx.text(value, font_size="28px", font_weight="700", color="#0F172A", letter_spacing="-0.02em"),
                rx.text(subtext, font_size="12px", color="#10B981", font_weight="500"),
                align_items="flex-start",
                spacing="1",
            ),
            rx.spacer(),
            rx.box(
                rx.icon(icon_name, size=24, color=color_hex),
                background=f"{color_hex}15",
                padding="12px",
                border_radius="12px",
            ),
            width="100%",
            align_items="center",
        ),
        width="100%",
    )


def dashboard_page() -> rx.Component:
    return rx.hstack(
        sidebar(current_page="dashboard", user_role=State.user_role),
        rx.vstack(
            navbar(user_name=State.user_name, user_role=State.user_role),
            rx.box(
                rx.vstack(
                    # Welcome Banner with animated subtle gradient
                    rx.box(
                        rx.hstack(
                            rx.vstack(
                                rx.text("Welcome back, Dr. Wright 👋", font_size="24px", font_weight="700", color="#0F172A"),
                                rx.text("Here is your clinical operations overview for today at Valley Clinic & Hospital.", font_size="14px", color="#475569"),
                                spacing="1",
                                align_items="flex-start",
                            ),
                            rx.spacer(),
                            rx.hstack(
                                rx.button(
                                    rx.icon("plus", size=16),
                                    "New Patient",
                                    background="#0D9488",
                                    color="white",
                                    border_radius="8px",
                                    padding="8px 16px",
                                    _hover={"background": "#0F766E"},
                                ),
                                rx.button(
                                    rx.icon("calendar-plus", size=16),
                                    "Book Appointment",
                                    background="#3B82F6",
                                    color="white",
                                    border_radius="8px",
                                    padding="8px 16px",
                                    _hover={"background": "#2563EB"},
                                ),
                                spacing="3",
                            ),
                            width="100%",
                            align_items="center",
                        ),
                        background="linear-gradient(135deg, #F0FDFA 0%, #EFF6FF 100%)",
                        padding="24px 32px",
                        border_radius="14px",
                        border="1px solid #CCFBF1",
                        width="100%",
                        margin_bottom="24px",
                    ),

                    # 4 Top KPI Cards
                    rx.grid(
                        kpi_card("Total Active Patients", "20", "+12% this month", "users", "#0D9488"),
                        kpi_card("Today's Appointments", "4 Scheduled", "3 confirmed", "calendar", "#3B82F6"),
                        kpi_card("Revenue This Month", "$18,450", "+8.4% vs last mo", "dollar-sign", "#10B981"),
                        kpi_card("Critical Alerts", "2 Items", "Immediate review", "alert-triangle", "#EF4444"),
                        columns="4",
                        spacing="4",
                        width="100%",
                        margin_bottom="24px",
                    ),

                    # 2 Main Content Columns: Analytics & Activity
                    rx.grid(
                        # Left Column: Charts / Analytics
                        animated_card(
                            rx.hstack(
                                rx.vstack(
                                    rx.text("Clinical Patient Visits", font_size="16px", font_weight="700", color="#0F172A"),
                                    rx.text("Daily appointment volume trends over the past 30 days", font_size="12px", color="#64748B"),
                                    spacing="0",
                                ),
                                rx.spacer(),
                                rx.badge("Live Realtime", color_scheme="teal"),
                                width="100%",
                                align_items="center",
                                margin_bottom="16px",
                            ),
                            # Visualization bar representation
                            rx.box(
                                rx.hstack(
                                    rx.vstack(rx.box(height="120px", width="24px", background="#0D9488", border_radius="4px"), rx.text("Mon", font_size="10px")),
                                    rx.vstack(rx.box(height="160px", width="24px", background="#3B82F6", border_radius="4px"), rx.text("Tue", font_size="10px")),
                                    rx.vstack(rx.box(height="90px", width="24px", background="#0D9488", border_radius="4px"), rx.text("Wed", font_size="10px")),
                                    rx.vstack(rx.box(height="190px", width="24px", background="#10B981", border_radius="4px"), rx.text("Thu", font_size="10px")),
                                    rx.vstack(rx.box(height="140px", width="24px", background="#0D9488", border_radius="4px"), rx.text("Fri", font_size="10px")),
                                    rx.vstack(rx.box(height="80px", width="24px", background="#F59E0B", border_radius="4px"), rx.text("Sat", font_size="10px")),
                                    spacing="5",
                                    align_items="flex-end",
                                    height="200px",
                                    justify_content="center",
                                    padding="16px",
                                    background="#F8FAFC",
                                    border_radius="10px",
                                ),
                                width="100%",
                            ),
                            width="100%",
                        ),

                        # Right Column: Recent Activity Feed
                        animated_card(
                            rx.hstack(
                                rx.text("Recent Clinical Activity", font_size="16px", font_weight="700", color="#0F172A"),
                                rx.spacer(),
                                rx.text("View all", font_size="12px", color="#3B82F6", font_weight="600"),
                                width="100%",
                                margin_bottom="16px",
                            ),
                            rx.vstack(
                                rx.hstack(
                                    rx.box("📅", background="#E0F2FE", padding="8px", border_radius="8px"),
                                    rx.vstack(
                                        rx.text("Appointment Confirmed", font_size="13px", font_weight="600"),
                                        rx.text("Eleanor Vance with Dr. Wright (Cardiology)", font_size="11px", color="#64748B"),
                                        spacing="0",
                                    ),
                                    rx.spacer(),
                                    rx.text("10m ago", font_size="11px", color="#94A3B8"),
                                    width="100%",
                                    align_items="center",
                                ),
                                rx.divider(),
                                rx.hstack(
                                    rx.box("💊", background="#ECFDF5", padding="8px", border_radius="8px"),
                                    rx.vstack(
                                        rx.text("Prescription Issued", font_size="13px", font_weight="600"),
                                        rx.text("Amoxicillin 500mg (21 qty) for Thomas Shelby", font_size="11px", color="#64748B"),
                                        spacing="0",
                                    ),
                                    rx.spacer(),
                                    rx.text("25m ago", font_size="11px", color="#94A3B8"),
                                    width="100%",
                                    align_items="center",
                                ),
                                rx.divider(),
                                rx.hstack(
                                    rx.box("🔬", background="#FEF3C7", padding="8px", border_radius="8px"),
                                    rx.vstack(
                                        rx.text("Lab Report Completed", font_size="13px", font_weight="600"),
                                        rx.text("Blood Work Panel uploaded for Arthur Pendelton", font_size="11px", color="#64748B"),
                                        spacing="0",
                                    ),
                                    rx.spacer(),
                                    rx.text("1h ago", font_size="11px", color="#94A3B8"),
                                    width="100%",
                                    align_items="center",
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            width="100%",
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    width="100%",
                    spacing="0",
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
