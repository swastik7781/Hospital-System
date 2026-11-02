import reflex as rx
from frontend.state import State
from frontend.components.sidebar import sidebar
from frontend.components.navbar import navbar
from frontend.components.animated_card import animated_card


def settings_page() -> rx.Component:
    return rx.hstack(
        sidebar(current_page="settings", user_role=State.user_role),
        rx.vstack(
            navbar(user_name=State.user_name, user_role=State.user_role),
            rx.box(
                rx.vstack(
                    rx.text("Account Settings & Security", font_size="22px", font_weight="700", color="#0F172A", margin_bottom="20px"),
                    rx.grid(
                        # Profile Settings Card
                        animated_card(
                            rx.vstack(
                                rx.text("User Profile Details", font_size="16px", font_weight="700", color="#0F172A"),
                                rx.text("Update your personal identity details and hospital contact phone", font_size="13px", color="#64748B"),
                                rx.divider(margin_y="12px"),
                                rx.vstack(
                                    rx.text("Full Name", font_size="13px", font_weight="600"),
                                    rx.input(value="Dr. Alexander Wright, MD", border_radius="8px"),
                                    align_items="flex-start",
                                    width="100%",
                                ),
                                rx.vstack(
                                    rx.text("Official Email", font_size="13px", font_weight="600"),
                                    rx.input(value="doctor@hospital.com", disabled=True, border_radius="8px", background="#F1F5F9"),
                                    align_items="flex-start",
                                    width="100%",
                                ),
                                rx.vstack(
                                    rx.text("Phone Number", font_size="13px", font_weight="600"),
                                    rx.input(value="+1 555-010-0002", border_radius="8px"),
                                    align_items="flex-start",
                                    width="100%",
                                ),
                                rx.button("Save Profile Changes", background="#0D9488", color="white", margin_top="12px"),
                                align_items="flex-start",
                                spacing="3",
                                width="100%",
                            ),
                            width="100%",
                        ),

                        # Password Change Card
                        animated_card(
                            rx.vstack(
                                rx.text("Change Password", font_size="16px", font_weight="700", color="#0F172A"),
                                rx.text("Ensure your password has at least 8 characters with numbers and symbols", font_size="13px", color="#64748B"),
                                rx.divider(margin_y="12px"),
                                rx.vstack(
                                    rx.text("Current Password", font_size="13px", font_weight="600"),
                                    rx.input(type="password", placeholder="••••••••", border_radius="8px"),
                                    align_items="flex-start",
                                    width="100%",
                                ),
                                rx.vstack(
                                    rx.text("New Password", font_size="13px", font_weight="600"),
                                    rx.input(type="password", placeholder="••••••••", border_radius="8px"),
                                    align_items="flex-start",
                                    width="100%",
                                ),
                                rx.vstack(
                                    rx.text("Confirm New Password", font_size="13px", font_weight="600"),
                                    rx.input(type="password", placeholder="••••••••", border_radius="8px"),
                                    align_items="flex-start",
                                    width="100%",
                                ),
                                rx.button("Update Password", variant="outline", color_scheme="teal", margin_top="12px"),
                                align_items="flex-start",
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
