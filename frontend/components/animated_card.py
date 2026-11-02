import reflex as rx


def animated_card(*children, **props) -> rx.Component:
    card_props = {
        "background": "#FFFFFF",
        "border_radius": "12px",
        "box_shadow": "0 4px 24px rgba(0, 0, 0, 0.06)",
        "border": "1px solid #E2E8F0",
        "padding": "24px",
        "transition": "all 0.25s cubic-bezier(0.16, 1, 0.3, 1)",
        "_hover": {
            "transform": "translateY(-3px)",
            "box_shadow": "0 12px 32px rgba(13, 148, 136, 0.09)",
            "border_color": "#CBD5E1",
        },
    }
    card_props.update(props)
    return rx.box(*children, **card_props)
