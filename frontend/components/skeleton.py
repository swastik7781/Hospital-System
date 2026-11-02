import reflex as rx


def skeleton_loader(width: str = "100%", height: str = "20px", border_radius: str = "8px") -> rx.Component:
    return rx.box(
        width=width,
        height=height,
        border_radius=border_radius,
        background="linear-gradient(90deg, #F1F5F9 25%, #E2E8F0 50%, #F1F5F9 75%)",
        background_size="200% 100%",
        animation="shimmer 1.6s infinite ease-in-out",
        margin_bottom="8px",
    )
