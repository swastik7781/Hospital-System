import reflex as rx
from frontend.state import State
from frontend.components.sidebar import sidebar
from frontend.components.navbar import navbar
from frontend.components.animated_card import animated_card
from frontend.components.status_badge import status_badge


def patients_page() -> rx.Component:
    sample_patients = [
        {"id": 1, "name": "Eleanor Vance", "age": "38", "gender": "Female", "phone": "+1 555-101-0001", "blood": "A+", "visits": 4},
        {"id": 2, "name": "Arthur Pendelton", "age": "51", "gender": "Male", "phone": "+1 555-101-0002", "blood": "O+", "visits": 2},
        {"id": 3, "name": "Clara Oswald", "age": "34", "gender": "Female", "phone": "+1 555-101-0003", "blood": "B+", "visits": 6},
        {"id": 4, "name": "Thomas Shelby", "age": "44", "gender": "Male", "phone": "+1 555-101-0004", "blood": "AB+", "visits": 5},
        {"id": 5, "name": "Grace Burgess", "age": "40", "gender": "Female", "phone": "+1 555-101-0005", "blood": "O-", "visits": 3},
    ]

    return rx.hstack(
        sidebar(current_page="patients", user_role=State.user_role),
        rx.vstack(
            navbar(user_name=State.user_name, user_role=State.user_role),
            rx.box(
                rx.vstack(
                    # Header
                    rx.hstack(
                        rx.vstack(
                            rx.text("Patients Directory", font_size="22px", font_weight="700", color="#0F172A"),
                            rx.text("Search, register and manage clinical health records", font_size="13px", color="#64748B"),
                            align_items="flex-start",
                            spacing="0",
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.icon("user-plus", size=16),
                            "Register Patient",
                            background="#0D9488",
                            color="white",
                            border_radius="8px",
                            padding="8px 18px",
                            _hover={"background": "#0F766E"},
                        ),
                        width="100%",
                        align_items="center",
                        margin_bottom="20px",
                    ),

                    # Filter / Search Bar
                    animated_card(
                        rx.hstack(
                            rx.input(
                                placeholder="Search by patient name, phone, or medical record ID...",
                                width="360px",
                                border="1px solid #CBD5E1",
                                border_radius="8px",
                                padding="8px 12px",
                                font_size="13px",
                            ),
                            rx.select(["All Genders", "Female", "Male"], default_value="All Genders"),
                            rx.select(["All Blood Groups", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"], default_value="All Blood Groups"),
                            rx.spacer(),
                            rx.text("Showing 20 Active Patients", font_size="12px", color="#64748B", font_weight="500"),
                            width="100%",
                            align_items="center",
                        ),
                        padding="16px",
                        margin_bottom="20px",
                        width="100%",
                    ),

                    # Patients Table Card
                    animated_card(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Patient"),
                                    rx.table.column_header_cell("Age / Gender"),
                                    rx.table.column_header_cell("Contact Phone"),
                                    rx.table.column_header_cell("Blood Group"),
                                    rx.table.column_header_cell("Visits"),
                                    rx.table.column_header_cell("Action"),
                                )
                            ),
                            rx.table.body(
                                *[
                                    rx.table.row(
                                        rx.table.cell(
                                            rx.hstack(
                                                rx.avatar(name=p["name"], size="2", background="#0D9488"),
                                                rx.vstack(
                                                    rx.text(p["name"], font_weight="600", font_size="14px", color="#0F172A"),
                                                    rx.text(f"MRN #{1000 + p['id']}", font_size="11px", color="#64748B"),
                                                    spacing="0",
                                                ),
                                                spacing="3",
                                                align_items="center",
                                            )
                                        ),
                                        rx.table.cell(f"{p['age']} yrs / {p['gender']}"),
                                        rx.table.cell(p["phone"]),
                                        rx.table.cell(
                                            rx.badge(p["blood"], color_scheme="red")
                                        ),
                                        rx.table.cell(f"{p['visits']} visits"),
                                        rx.table.cell(
                                            rx.link(
                                                rx.button("View Chart", size="1", variant="outline", color_scheme="teal"),
                                                href=f"/patients/{p['id']}",
                                            )
                                        ),
                                    )
                                    for p in sample_patients
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
