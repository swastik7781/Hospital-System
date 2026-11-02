import reflex as rx
from frontend.state import State
from frontend.components.sidebar import sidebar
from frontend.components.navbar import navbar
from frontend.components.animated_card import animated_card
from frontend.components.status_badge import status_badge


def patient_detail_page() -> rx.Component:
    return rx.hstack(
        sidebar(current_page="patients", user_role=State.user_role),
        rx.vstack(
            navbar(user_name=State.user_name, user_role=State.user_role),
            rx.box(
                rx.vstack(
                    # Back navigation link
                    rx.link(
                        rx.hstack(
                            rx.icon("arrow-left", size=16),
                            rx.text("Back to Patients", font_size="13px", font_weight="500"),
                            spacing="2",
                            align_items="center",
                            color="#64748B",
                        ),
                        href="/patients",
                        margin_bottom="16px",
                    ),

                    # Patient Banner Card
                    animated_card(
                        rx.hstack(
                            rx.avatar(name="Eleanor Vance", size="5", background="#0D9488"),
                            rx.vstack(
                                rx.hstack(
                                    rx.text("Eleanor Vance", font_size="22px", font_weight="700", color="#0F172A"),
                                    rx.badge("Active Patient", color_scheme="green"),
                                    rx.badge("Blood: A+", color_scheme="red"),
                                    align_items="center",
                                    spacing="2",
                                ),
                                rx.hstack(
                                    rx.text("MRN: #1001", font_size="12px", color="#64748B"),
                                    rx.text("•", color="#CBD5E1"),
                                    rx.text("DOB: Apr 12, 1988 (38 yrs)", font_size="12px", color="#64748B"),
                                    rx.text("•", color="#CBD5E1"),
                                    rx.text("Phone: +1 555-101-0001", font_size="12px", color="#64748B"),
                                    rx.text("•", color="#CBD5E1"),
                                    rx.text("Allergies: Penicillin", font_size="12px", color="#DC2626", font_weight="600"),
                                    spacing="2",
                                ),
                                spacing="1",
                                align_items="flex-start",
                            ),
                            rx.spacer(),
                            rx.hstack(
                                rx.button("Edit Profile", variant="outline", size="2"),
                                rx.button("Book Visit", background="#0D9488", color="white", size="2"),
                                spacing="2",
                            ),
                            width="100%",
                            align_items="center",
                        ),
                        margin_bottom="24px",
                        width="100%",
                    ),

                    # Tabs Container (Overview, Visits, Prescriptions, Reports, Invoices)
                    rx.tabs.root(
                        rx.tabs.list(
                            rx.tabs.trigger("Overview", value="overview"),
                            rx.tabs.trigger("Clinical Visits (4)", value="visits"),
                            rx.tabs.trigger("Prescriptions (2)", value="prescriptions"),
                            rx.tabs.trigger("Lab Reports (3)", value="reports"),
                            rx.tabs.trigger("Billing & Invoices (2)", value="billing"),
                        ),
                        rx.tabs.content(
                            # Overview tab content
                            animated_card(
                                rx.vstack(
                                    rx.text("Medical History Summary", font_size="16px", font_weight="700", color="#0F172A"),
                                    rx.text("Mild essential hypertension diagnosed in 2021. Managed with low-sodium diet and lifestyle exercise. No surgical interventions.", font_size="14px", color="#475569"),
                                    rx.divider(margin_y="16px"),
                                    rx.text("Emergency Contact Information", font_size="16px", font_weight="700", color="#0F172A"),
                                    rx.text("Spouse: Robert Vance — Phone: +1 555-999-0000", font_size="14px", color="#475569"),
                                    align_items="flex-start",
                                    spacing="2",
                                    width="100%",
                                ),
                                margin_top="16px",
                                width="100%",
                            ),
                            value="overview",
                        ),
                        rx.tabs.content(
                            animated_card(
                                rx.text("Visit Records linked to Eleanor Vance", font_size="16px", font_weight="700", margin_bottom="12px"),
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Date"),
                                            rx.table.column_header_cell("Attending Doctor"),
                                            rx.table.column_header_cell("Reason"),
                                            rx.table.column_header_cell("Status"),
                                            rx.table.column_header_cell("Diagnosis"),
                                        )
                                    ),
                                    rx.table.body(
                                        rx.table.row(
                                            rx.table.cell("2026-10-15"),
                                            rx.table.cell("Dr. Alexander Wright"),
                                            rx.table.cell("Routine cardiology consultation"),
                                            rx.table.cell(status_badge("completed")),
                                            rx.table.cell("Mild essential hypertension"),
                                        ),
                                        rx.table.row(
                                            rx.table.cell("2026-10-24"),
                                            rx.table.cell("Dr. Alexander Wright"),
                                            rx.table.cell("Follow-up blood pressure check"),
                                            rx.table.cell(status_badge("confirmed")),
                                            rx.table.cell("-"),
                                        ),
                                    ),
                                    width="100%",
                                ),
                                margin_top="16px",
                                width="100%",
                            ),
                            value="visits",
                        ),
                        default_value="overview",
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
