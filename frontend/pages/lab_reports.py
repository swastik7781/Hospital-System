import reflex as rx
from frontend.state import State
from frontend.components.sidebar import sidebar
from frontend.components.navbar import navbar
from frontend.components.animated_card import animated_card
from frontend.components.status_badge import status_badge


def lab_reports_page() -> rx.Component:
    sample_tests = [
        {"id": 1, "patient": "Eleanor Vance", "doctor": "Dr. Wright", "type": "Blood Work", "date": "2026-10-23", "status": "completed", "critical": False, "findings": "All parameters normal"},
        {"id": 2, "patient": "Arthur Pendelton", "doctor": "Dr. Chen", "type": "MRI Scan", "date": "2026-10-22", "status": "completed", "critical": False, "findings": "No acute intracranial hemorrhage"},
        {"id": 3, "patient": "Clara Oswald", "doctor": "Dr. Kim", "type": "Blood Work", "date": "2026-10-21", "status": "completed", "critical": True, "findings": "Low platelet count (55k/uL) - Critical flag!"},
        {"id": 4, "patient": "Thomas Shelby", "doctor": "Dr. Chang", "type": "X-Ray", "date": "2026-10-20", "status": "in_progress", "critical": False, "findings": "Radiologist review in progress"},
    ]

    return rx.hstack(
        sidebar(current_page="lab_reports", user_role=State.user_role),
        rx.vstack(
            navbar(user_name=State.user_name, user_role=State.user_role),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.text("Diagnostic Lab Tests & Radiology", font_size="22px", font_weight="700", color="#0F172A"),
                            rx.text("Order lab diagnostics, manage workflow, flag abnormal findings, and upload report documents", font_size="13px", color="#64748B"),
                            align_items="flex-start",
                            spacing="0",
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.icon("flask-conical", size=16),
                            "Order Lab Test",
                            background="#0D9488",
                            color="white",
                            border_radius="8px",
                            padding="8px 18px",
                        ),
                        width="100%",
                        align_items="center",
                        margin_bottom="24px",
                    ),

                    # Lab Reports Table
                    animated_card(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Test ID"),
                                    rx.table.column_header_cell("Patient"),
                                    rx.table.column_header_cell("Test Modality"),
                                    rx.table.column_header_cell("Ordered By"),
                                    rx.table.column_header_cell("Scheduled Date"),
                                    rx.table.column_header_cell("Status"),
                                    rx.table.column_header_cell("Findings"),
                                    rx.table.column_header_cell("Action"),
                                )
                            ),
                            rx.table.body(
                                *[
                                    rx.table.row(
                                        rx.table.cell(f"#{t['id']}"),
                                        rx.table.cell(rx.text(t["patient"], font_weight="600")),
                                        rx.table.cell(rx.badge(t["type"], color_scheme="blue")),
                                        rx.table.cell(t["doctor"]),
                                        rx.table.cell(t["date"]),
                                        rx.table.cell(status_badge(t["status"])),
                                        rx.table.cell(
                                            rx.hstack(
                                                rx.cond(t["critical"], rx.badge("CRITICAL", color_scheme="red")),
                                                rx.text(t["findings"], font_size="13px"),
                                                spacing="2",
                                                align_items="center",
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.button(
                                                rx.icon("upload", size=14),
                                                "Upload Report",
                                                size="1",
                                                variant="outline",
                                                color_scheme="teal",
                                            )
                                        ),
                                    )
                                    for t in sample_tests
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
