import reflex as rx


def status_badge(status_text: str, badge_type: str = "default") -> rx.Component:
    color_map = {
        "completed": {"bg": "#DEF7EC", "color": "#03543F", "border": "#BCF0DA"},
        "confirmed": {"bg": "#E1EFFE", "color": "#1E429F", "border": "#B4C6FC"},
        "scheduled": {"bg": "#FEF08A", "color": "#854D0E", "border": "#FDE047"},
        "in_progress": {"bg": "#E0E7FF", "color": "#3730A3", "border": "#C7D2FE"},
        "cancelled": {"bg": "#FDE8E8", "color": "#9B1C1C", "border": "#F8B4B4"},
        "no_show": {"bg": "#F3F4F6", "color": "#374151", "border": "#E5E7EB"},
        "paid": {"bg": "#DEF7EC", "color": "#03543F", "border": "#BCF0DA"},
        "pending": {"bg": "#FEF3C7", "color": "#92400E", "border": "#FDE68A"},
        "partial": {"bg": "#FEE2E2", "color": "#991B1B", "border": "#FECACA"},
    }
    
    style = color_map.get(status_text.lower(), {"bg": "#F3F4F6", "color": "#4B5563", "border": "#E5E7EB"})
    
    return rx.box(
        rx.text(status_text.replace("_", " ").upper(), font_size="11px", font_weight="700", letter_spacing="0.05em"),
        background=style["bg"],
        color=style["color"],
        border=f"1px solid {style['border']}",
        padding="3px 10px",
        border_radius="9999px",
        display="inline-flex",
        align_items="center",
        transition="all 0.2s ease-in-out",
    )
