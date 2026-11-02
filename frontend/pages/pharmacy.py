import reflex as rx
from frontend.state import State
from frontend.components.sidebar import sidebar
from frontend.components.navbar import navbar
from frontend.components.animated_card import animated_card


def pharmacy_page() -> rx.Component:
    sample_medicines = [
        {"id": 1, "name": "Amoxicillin 500mg", "generic": "Amoxicillin", "cat": "Antibiotic", "unit": "capsule", "stock": 150, "reorder": 50, "status": "In Stock"},
        {"id": 2, "name": "Paracetamol 650mg", "generic": "Acetaminophen", "cat": "Analgesic", "unit": "tablet", "stock": 400, "reorder": 100, "status": "In Stock"},
        {"id": 3, "name": "Morphine Sulfate 10mg", "generic": "Morphine", "cat": "Analgesic", "unit": "ampoule", "stock": 8, "reorder": 10, "status": "Low Stock"},
        {"id": 4, "name": "Ceftriaxone 1g", "generic": "Ceftriaxone", "cat": "Antibiotic", "unit": "vial", "stock": 12, "reorder": 20, "status": "Low Stock"},
    ]

    return rx.hstack(
        sidebar(current_page="pharmacy", user_role=State.user_role),
        rx.vstack(
            navbar(user_name=State.user_name, user_role=State.user_role),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.text("Pharmacy & Inventory Dispensary", font_size="22px", font_weight="700", color="#0F172A"),
                            rx.text("Manage pharmaceutical inventory, track batch expiry, dispense medicines, and monitor alerts", font_size="13px", color="#64748B"),
                            align_items="flex-start",
                            spacing="0",
                        ),
                        rx.spacer(),
                        rx.hstack(
                            rx.button(
                                rx.icon("arrow-down-left", size=16),
                                "Stock In (Purchase)",
                                background="#3B82F6",
                                color="white",
                                border_radius="8px",
                            ),
                            rx.button(
                                rx.icon("arrow-up-right", size=16),
                                "Dispense (Stock Out)",
                                background="#0D9488",
                                color="white",
                                border_radius="8px",
                            ),
                            spacing="2",
                        ),
                        width="100%",
                        align_items="center",
                        margin_bottom="20px",
                    ),

                    # Low Stock & Expiry Alert Banner
                    rx.box(
                        rx.hstack(
                            rx.box("⚠️", font_size="20px"),
                            rx.vstack(
                                rx.text("Low Stock & Expiry Warning Notice", font_weight="700", font_size="14px", color="#991B1B"),
                                rx.text("2 medicines are below clinical reorder levels (Morphine, Ceftriaxone) and 2 batches expire within 30 days.", font_size="13px", color="#B91C1C"),
                                spacing="0",
                                align_items="flex-start",
                            ),
                            rx.spacer(),
                            rx.button("Reorder Items", size="1", color_scheme="red", variant="solid"),
                            align_items="center",
                            width="100%",
                        ),
                        background="#FEF2F2",
                        border="1px solid #FECACA",
                        padding="16px 20px",
                        border_radius="12px",
                        width="100%",
                        margin_bottom="20px",
                    ),

                    # Inventory Table
                    animated_card(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Medicine Name"),
                                    rx.table.column_header_cell("Generic / Formula"),
                                    rx.table.column_header_cell("Category"),
                                    rx.table.column_header_cell("Unit"),
                                    rx.table.column_header_cell("Current Stock"),
                                    rx.table.column_header_cell("Reorder Level"),
                                    rx.table.column_header_cell("Status"),
                                    rx.table.column_header_cell("Action"),
                                )
                            ),
                            rx.table.body(
                                *[
                                    rx.table.row(
                                        rx.table.cell(rx.text(m["name"], font_weight="600")),
                                        rx.table.cell(m["generic"]),
                                        rx.table.cell(rx.badge(m["cat"], color_scheme="teal")),
                                        rx.table.cell(m["unit"]),
                                        rx.table.cell(rx.text(str(m["stock"]), font_weight="700")),
                                        rx.table.cell(str(m["reorder"])),
                                        rx.table.cell(
                                            rx.cond(
                                                m["status"] == "Low Stock",
                                                rx.badge("LOW STOCK", color_scheme="red"),
                                                rx.badge("IN STOCK", color_scheme="green"),
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.button("Batches", size="1", variant="outline")
                                        ),
                                    )
                                    for m in sample_medicines
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
