import reflex as rx
from frontend.state import State
from frontend.components.sidebar import sidebar
from frontend.components.navbar import navbar
from frontend.components.animated_card import animated_card


def prescriptions_page() -> rx.Component:
    sample_prescriptions = [
        {"id": 1, "patient": "Eleanor Vance", "doctor": "Dr. Alexander Wright", "date": "2026-10-23", "items": "Amoxicillin 500mg (21), Paracetamol (10)"},
        {"id": 2, "patient": "Arthur Pendelton", "doctor": "Dr. Robert Chen", "date": "2026-10-22", "items": "Gabapentin 300mg (30)"},
        {"id": 3, "patient": "Clara Oswald", "doctor": "Dr. David Kim", "date": "2026-10-21", "items": "Albuterol Inhaler (1), Cetirizine (14)"},
        {"id": 4, "patient": "Thomas Shelby", "doctor": "Dr. Michael Chang", "date": "2026-10-20", "items": "Ibuprofen 400mg (20)"},
    ]

    return rx.hstack(
        sidebar(current_page="prescriptions", user_role=State.user_role),
        rx.vstack(
            navbar(user_name=State.user_name, user_role=State.user_role),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.text("Clinical Prescriptions (℞)", font_size="22px", font_weight="700", color="#0F172A"),
                            rx.text("Create medications, manage line items, and generate official printable PDF orders", font_size="13px", color="#64748B"),
                            align_items="flex-start",
                            spacing="0",
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.icon("plus", size=16),
                            "Issue New Prescription",
                            background="#0D9488",
                            color="white",
                            border_radius="8px",
                            padding="8px 18px",
                        ),
                        width="100%",
                        align_items="center",
                        margin_bottom="24px",
                    ),

                    # Prescriptions Table Card
                    animated_card(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Rx ID"),
                                    rx.table.column_header_cell("Patient"),
                                    rx.table.column_header_cell("Prescribing Doctor"),
                                    rx.table.column_header_cell("Date"),
                                    rx.table.column_header_cell("Prescribed Medications"),
                                    rx.table.column_header_cell("Printable PDF"),
                                )
                            ),
                            rx.table.body(
                                *[
                                    rx.table.row(
                                        rx.table.cell(f"℞ #{p['id']}"),
                                        rx.table.cell(rx.text(p["patient"], font_weight="600")),
                                        rx.table.cell(p["doctor"]),
                                        rx.table.cell(p["date"]),
                                        rx.table.cell(p["items"]),
                                        rx.table.cell(
                                            rx.link(
                                                rx.button(
                                                    rx.icon("file-down", size=14),
                                                    "Download PDF",
                                                    size="1",
                                                    color_scheme="teal",
                                                    variant="soft",
                                                ),
                                                href=f"http://localhost:8000/api/v1/prescriptions/{p['id']}/pdf",
                                                is_external=True,
                                            )
                                        ),
                                    )
                                    for p in sample_prescriptions
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
