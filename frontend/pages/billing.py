import reflex as rx
from frontend.state import State
from frontend.components.sidebar import sidebar
from frontend.components.navbar import navbar
from frontend.components.animated_card import animated_card
from frontend.components.status_badge import status_badge


def billing_page() -> rx.Component:
    sample_invoices = [
        {"id": 1, "inv_no": "INV-20261023-1001", "patient": "Eleanor Vance", "total": "$204.75", "paid": "$204.75", "method": "Card", "status": "paid"},
        {"id": 2, "inv_no": "INV-20261023-1002", "patient": "Arthur Pendelton", "total": "$215.25", "paid": "$215.25", "method": "Insurance", "status": "paid"},
        {"id": 3, "inv_no": "INV-20261023-1003", "patient": "Clara Oswald", "total": "$236.25", "paid": "$118.00", "method": "Cash", "status": "partial"},
        {"id": 4, "inv_no": "INV-20261023-1004", "patient": "Thomas Shelby", "total": "$246.75", "paid": "$0.00", "method": "Online", "status": "pending"},
    ]

    return rx.hstack(
        sidebar(current_page="billing", user_role=State.user_role),
        rx.vstack(
            navbar(user_name=State.user_name, user_role=State.user_role),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.text("Billing & Financial Revenue", font_size="22px", font_weight="700", color="#0F172A"),
                            rx.text("Generate medical invoices, track payments, insurance claims, and revenue growth", font_size="13px", color="#64748B"),
                            align_items="flex-start",
                            spacing="0",
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.icon("receipt", size=16),
                            "Generate Invoice",
                            background="#0D9488",
                            color="white",
                            border_radius="8px",
                            padding="8px 18px",
                        ),
                        width="100%",
                        align_items="center",
                        margin_bottom="24px",
                    ),

                    # 3 Metric Cards
                    rx.grid(
                        animated_card(
                            rx.text("Collected Revenue Today", font_size="13px", color="#64748B"),
                            rx.text("$1,420.00", font_size="26px", font_weight="700", color="#10B981"),
                            rx.text("6 invoices processed", font_size="12px", color="#64748B"),
                        ),
                        animated_card(
                            rx.text("Collected This Month", font_size="13px", color="#64748B"),
                            rx.text("$18,450.00", font_size="26px", font_weight="700", color="#0F172A"),
                            rx.text("+14.2% vs previous month", font_size="12px", color="#10B981"),
                        ),
                        animated_card(
                            rx.text("Pending Receivables", font_size="13px", color="#64748B"),
                            rx.text("$1,860.50", font_size="26px", font_weight="700", color="#F59E0B"),
                            rx.text("4 pending / partial bills", font_size="12px", color="#64748B"),
                        ),
                        columns="3",
                        spacing="4",
                        width="100%",
                        margin_bottom="24px",
                    ),

                    # Invoices Table
                    animated_card(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Invoice No"),
                                    rx.table.column_header_cell("Patient"),
                                    rx.table.column_header_cell("Total Amount"),
                                    rx.table.column_header_cell("Amount Paid"),
                                    rx.table.column_header_cell("Payment Method"),
                                    rx.table.column_header_cell("Status"),
                                    rx.table.column_header_cell("Action"),
                                )
                            ),
                            rx.table.body(
                                *[
                                    rx.table.row(
                                        rx.table.cell(rx.text(inv["inv_no"], font_family="monospace", font_weight="600")),
                                        rx.table.cell(inv["patient"]),
                                        rx.table.cell(rx.text(inv["total"], font_weight="700")),
                                        rx.table.cell(inv["paid"]),
                                        rx.table.cell(rx.badge(inv["method"], color_scheme="gray")),
                                        rx.table.cell(status_badge(inv["status"])),
                                        rx.table.cell(
                                            rx.button("Record Payment", size="1", color_scheme="teal", variant="outline")
                                        ),
                                    )
                                    for inv in sample_invoices
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
