import reflex as rx
from frontend.state import State
from frontend.components.sidebar import sidebar
from frontend.components.navbar import navbar
from frontend.components.animated_card import animated_card
from frontend.components.status_badge import status_badge


def appointments_page() -> rx.Component:
    sample_appointments = [
        {"id": 101, "patient": "Eleanor Vance", "doctor": "Dr. Alexander Wright", "date": "2026-10-24", "time": "09:30", "reason": "Follow-up BP check", "status": "confirmed"},
        {"id": 102, "patient": "Arthur Pendelton", "doctor": "Dr. Robert Chen", "date": "2026-10-24", "time": "10:30", "reason": "Migraine checkup", "status": "scheduled"},
        {"id": 103, "patient": "Clara Oswald", "doctor": "Dr. David Kim", "date": "2026-10-24", "time": "11:00", "reason": "Pediatric evaluation", "status": "in_progress"},
        {"id": 104, "patient": "Thomas Shelby", "doctor": "Dr. Michael Chang", "date": "2026-10-23", "time": "14:00", "reason": "Rotator cuff post-op", "status": "completed"},
        {"id": 105, "patient": "Grace Burgess", "doctor": "Dr. Jessica Taylor", "date": "2026-10-23", "time": "15:30", "reason": "Knee pain assessment", "status": "no_show"},
    ]

    return rx.hstack(
        sidebar(current_page="appointments", user_role=State.user_role),
        rx.vstack(
            navbar(user_name=State.user_name, user_role=State.user_role),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.text("Clinical Appointments & Visits", font_size="22px", font_weight="700", color="#0F172A"),
                            rx.text("Real-time scheduling grid with conflict detection and automated recurring visits", font_size="13px", color="#64748B"),
                            align_items="flex-start",
                            spacing="0",
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.icon("calendar-plus", size=16),
                            "Book Appointment",
                            background="#0D9488",
                            color="white",
                            border_radius="8px",
                            padding="8px 18px",
                        ),
                        width="100%",
                        align_items="center",
                        margin_bottom="20px",
                    ),

                    # Filter Bar
                    animated_card(
                        rx.hstack(
                            rx.select(["All Statuses", "scheduled", "confirmed", "in_progress", "completed", "cancelled", "no_show"], default_value="All Statuses"),
                            rx.select(["All Doctors", "Dr. Alexander Wright", "Dr. Maria Rodriguez", "Dr. Robert Chen", "Dr. David Kim"], default_value="All Doctors"),
                            rx.input(type="date", width="180px", border="1px solid #CBD5E1", border_radius="8px"),
                            rx.spacer(),
                            rx.segmented_control.root(
                                rx.segmented_control.item("List View", value="list"),
                                rx.segmented_control.item("Calendar View", value="calendar"),
                                default_value="list",
                            ),
                            width="100%",
                            align_items="center",
                        ),
                        padding="16px",
                        margin_bottom="20px",
                        width="100%",
                    ),

                    # Appointments Table Card
                    animated_card(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Appointment ID"),
                                    rx.table.column_header_cell("Patient"),
                                    rx.table.column_header_cell("Attending Doctor"),
                                    rx.table.column_header_cell("Date & Slot"),
                                    rx.table.column_header_cell("Reason"),
                                    rx.table.column_header_cell("Status"),
                                    rx.table.column_header_cell("Action"),
                                )
                            ),
                            rx.table.body(
                                *[
                                    rx.table.row(
                                        rx.table.cell(f"#{a['id']}"),
                                        rx.table.cell(rx.text(a["patient"], font_weight="600")),
                                        rx.table.cell(a["doctor"]),
                                        rx.table.cell(f"{a['date']} at {a['time']}"),
                                        rx.table.cell(a["reason"]),
                                        rx.table.cell(status_badge(a["status"])),
                                        rx.table.cell(
                                            rx.hstack(
                                                rx.button("Complete", size="1", color_scheme="teal", variant="solid"),
                                                rx.button("Reschedule", size="1", variant="outline"),
                                                spacing="2",
                                            )
                                        ),
                                    )
                                    for a in sample_appointments
                                ]
                            ),
                            width="100%",
                        ),
                        width="100%",
                        padding="0",
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
