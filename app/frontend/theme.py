"""Central theme constants. Single source of truth for colors, radii and spacing.

Palette mirrors Programa Incluir's web app (app.programaincluir.org): a warm
orange brand accent over neutral grays, flat white surfaces with a hairline
border instead of heavy shadows.
"""

import flet as ft

# Brand accent
PRIMARY = "#E8622C"
PRIMARY_DARK = "#C94F1F"
PRIMARY_LIGHT = "#FDEEE3"
PRIMARY_GRADIENT = ["#E8622C", "#F4A15B"]

# Status colors
SUCCESS = "#2E7D32"
SUCCESS_LIGHT = "#E8F5E9"
ERROR = "#D64545"
ERROR_LIGHT = "#FBEAEA"

# Text
TEXT_PRIMARY = "#181411"
TEXT_SECONDARY = "#6B7280"
MUTED = TEXT_SECONDARY
MUTED_700 = "#4B5563"

# Surfaces
BORDER = "#E5E3E0"
SURFACE = "#FFFFFF"
BACKGROUND = "#F7F7F5"

# Shape
CARD_RADIUS = 16
INPUT_RADIUS = 12
PILL_RADIUS = 20
STEP_RADIUS = 15

# Spacing
SPACING_SM = 4
SPACING_MD = 8
SPACING_LG = 12
SPACING_XL = 24


def card(content: ft.Control, *, padding: int = 20, radius: int | None = None) -> ft.Container:
    """Flat white card with a hairline border (no drop shadow)."""
    return ft.Container(
        content=content,
        padding=padding,
        border_radius=radius if radius is not None else CARD_RADIUS,
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
    )


def responsive(
    content: ft.Control, *, col: dict | None = None, expand: bool = False
) -> ft.Control:
    """Full-width on mobile, centered max-width column on desktop."""
    return ft.ResponsiveRow(
        alignment=ft.MainAxisAlignment.CENTER,
        expand=expand,
        controls=[
            ft.Container(
                col=col or {"xs": 12, "sm": 11, "md": 8, "lg": 6, "xl": 5},
                content=content,
                expand=expand,
            )
        ],
    )


def page_theme() -> ft.Theme:
    """Material theme wiring the brand palette into every default control."""
    return ft.Theme(
        use_material3=True,
        color_scheme=ft.ColorScheme(
            primary=PRIMARY,
            on_primary=ft.Colors.WHITE,
            primary_container=PRIMARY_LIGHT,
            on_primary_container=PRIMARY_DARK,
            secondary=PRIMARY,
            on_secondary=ft.Colors.WHITE,
            error=ERROR,
            on_error=ft.Colors.WHITE,
            surface=SURFACE,
            on_surface=TEXT_PRIMARY,
            outline=BORDER,
            outline_variant=BORDER,
        ),
        card_theme=ft.CardTheme(
            color=SURFACE,
            elevation=0,
            shape=ft.RoundedRectangleBorder(radius=CARD_RADIUS),
        ),
        appbar_theme=ft.AppBarTheme(
            bgcolor=SURFACE,
            color=TEXT_PRIMARY,
            elevation=0,
        ),
        filled_button_theme=ft.FilledButtonTheme(
            style=ft.ButtonStyle(
                bgcolor=PRIMARY,
                color=ft.Colors.WHITE,
                padding=ft.Padding.symmetric(vertical=8, horizontal=20),
                shape=ft.RoundedRectangleBorder(radius=INPUT_RADIUS),
            )
        ),
        outlined_button_theme=ft.OutlinedButtonTheme(
            style=ft.ButtonStyle(
                color=TEXT_PRIMARY,
                side=ft.BorderSide(1, BORDER),
                padding=ft.Padding.symmetric(vertical=8, horizontal=20),
                shape=ft.RoundedRectangleBorder(radius=INPUT_RADIUS),
            )
        ),
        text_button_theme=ft.TextButtonTheme(
            style=ft.ButtonStyle(color=PRIMARY)
        ),
        progress_indicator_theme=ft.ProgressIndicatorTheme(color=PRIMARY),
        divider_color=BORDER,
    )
