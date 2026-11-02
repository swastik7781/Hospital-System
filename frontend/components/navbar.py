import reflex as rx


def navbar(user_name: str = "Admin User", user_role: str = "admin") -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon("search", size=18, color="#94A3B8"),
                rx.input(
                    placeholder="Search patients, doctors, appointments, medicines... (Ctrl+K)",
                    border="none",
                    background="transparent",
                    _focus={"outline": "none"},
                    width="400px",
                    font_size="14px",
                ),
                align_items="center",
                background="#F1F5F9",
                padding="6px 14px",
                border_radius="8px",
            ),
            rx.spacer(),
            rx.hstack(
                # System Status Live Pill
                rx.hstack(
                    rx.box(width="8px", height="8px", border_radius="50%", background="#10B981", animation="pulse 2s infinite"),
                    rx.text("Live EHR System", font_size="12px", font_weight="600", color="#065F46"),
                    background="#D1FAE5",
                    padding="4px 10px",
                    border_radius="9999px",
                    align_items="center",
                ),
                # User Profile pill
                rx.hstack(
                    rx.avatar(name=user_name, size="2", background="#0D9488"),
                    rx.vstack(
                        rx.text(user_name, font_size="13px", font_weight="600", color="#1E293B"),
                        rx.text(user_role.upper(), font_size="10px", font_weight="700", color="#0D9488"),
                        spacing="0",
                    ),
                    spacing="2",
                    align_items="center",
                    padding="4px 8px",
                    border_radius="8px",
                    _hover={"background": "#F8FAFC"},
                ),
                spacing="4",
                align_items="center",
            ),
            width="100%",
            align_items="center",
            padding="14px 32px",
        ),
        background="#FFFFFF",
        border_bottom="1px solid #E2E8F0",
        width="100%",
    )
