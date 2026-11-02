import reflex as rx
from frontend.state import State


def login_page() -> rx.Component:
    return rx.box(
        rx.center(
            rx.vstack(
                # Hospital Logo & Heading
                rx.vstack(
                    rx.box(
                        rx.text("🏥", font_size="32px"),
                        background="#CCFBF1",
                        padding="14px",
                        border_radius="18px",
                        box_shadow="0 8px 24px rgba(13, 148, 136, 0.2)",
                    ),
                    rx.text("Utkal Hospital & Medical Research Centre", font_size="24px", font_weight="800", color="#0F172A", letter_spacing="-0.02em"),
                    rx.text("Secure Clinical Access Portal", font_size="14px", color="#64748B"),
                    align_items="center",
                    spacing="2",
                    margin_bottom="12px",
                ),

                # Login Card
                rx.box(
                    rx.vstack(
                        rx.cond(
                            State.login_error != "",
                            rx.box(
                                rx.text(State.login_error, font_size="13px", color="#DC2626"),
                                background="#FEF2F2",
                                border="1px solid #FCA5A5",
                                padding="10px 14px",
                                border_radius="8px",
                                width="100%",
                            ),
                        ),

                        # Email
                        rx.vstack(
                            rx.text("Email Address", font_size="13px", font_weight="600", color="#334155"),
                            rx.input(
                                value=State.login_email,
                                on_change=State.set_login_email,
                                placeholder="name@hospital.com",
                                width="100%",
                                padding="12px 14px",
                                border_radius="8px",
                                border="1px solid #CBD5E1",
                                _focus={"border_color": "#0D9488", "box_shadow": "0 0 0 3px rgba(13, 148, 136, 0.15)"},
                            ),
                            align_items="flex-start",
                            width="100%",
                            spacing="1",
                        ),

                        # Password
                        rx.vstack(
                            rx.hstack(
                                rx.text("Password", font_size="13px", font_weight="600", color="#334155"),
                                rx.spacer(),
                                rx.link("Forgot?", font_size="12px", color="#3B82F6"),
                                width="100%",
                            ),
                            rx.input(
                                value=State.login_password,
                                on_change=State.set_login_password,
                                type="password",
                                placeholder="••••••••",
                                width="100%",
                                padding="12px 14px",
                                border_radius="8px",
                                border="1px solid #CBD5E1",
                                _focus={"border_color": "#0D9488", "box_shadow": "0 0 0 3px rgba(13, 148, 136, 0.15)"},
                            ),
                            align_items="flex-start",
                            width="100%",
                            spacing="1",
                        ),

                        # Submit Button
                        rx.button(
                            "Sign In to Utkal Portal",
                            on_click=State.login,
                            width="100%",
                            background="#0D9488",
                            color="white",
                            font_weight="600",
                            padding="14px",
                            border_radius="8px",
                            margin_top="10px",
                            _hover={"background": "#0F766E", "transform": "scale(0.99)"},
                            transition="all 0.15s ease",
                        ),

                        # Quick Demo Role Switcher
                        rx.divider(margin_y="16px"),
                        rx.text("Quick Login As:", font_size="12px", font_weight="600", color="#64748B"),
                        rx.hstack(
                            rx.badge("Admin", color_scheme="teal", cursor="pointer", on_click=lambda: State.set_role("admin")),
                            rx.badge("Doctor", color_scheme="blue", cursor="pointer", on_click=lambda: State.set_role("doctor")),
                            rx.badge("Receptionist", color_scheme="purple", cursor="pointer", on_click=lambda: State.set_role("receptionist")),
                            rx.badge("Patient", color_scheme="green", cursor="pointer", on_click=lambda: State.set_role("patient")),
                            spacing="2",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    background="#FFFFFF",
                    padding="36px 32px",
                    border_radius="16px",
                    box_shadow="0 10px 40px rgba(0, 0, 0, 0.08)",
                    border="1px solid #E2E8F0",
                    width="420px",
                ),

                # ECG Heartbeat Line Decorative SVG
                rx.box(
                    rx.html(
                        """
                        <svg width="240" height="40" viewBox="0 0 240 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M0 20H80L90 5L105 35L115 15L125 25L135 20H240" stroke="#0D9488" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        """
                    ),
                    margin_top="24px",
                    opacity="0.8",
                ),
                align_items="center",
                spacing="0",
            ),
            min_height="100vh",
            padding="40px",
        ),
        background="linear-gradient(135deg, #F8FAFC 0%, #E6FFFA 50%, #EFF6FF 100%)",
        min_height="100vh",
        width="100vw",
    )
