"""Step-dots progress indicator for the question wizard."""

from __future__ import annotations

import flet as ft

import theme


def build_progress(indices: int, answers: dict, current: int) -> ft.Control:
    """Render one dot per question: green answered, blue current, grey pending."""
    dots = []
    for i in range(indices):
        done = i < current or i in answers
        is_current = i == current
        background = (
            theme.SUCCESS
            if done and not is_current
            else (theme.PRIMARY if is_current else ft.Colors.GREY_300)
        )
        foreground = ft.Colors.WHITE if done or is_current else ft.Colors.BLACK_54
        dots.append(
            ft.Container(
                width=30,
                height=30,
                border_radius=theme.STEP_RADIUS,
                bgcolor=background,
                alignment=ft.Alignment.CENTER,
                content=ft.Text(
                    str(i + 1), color=foreground, weight=ft.FontWeight.BOLD
                ),
            )
        )
    return ft.Row(dots, alignment=ft.MainAxisAlignment.CENTER, spacing=theme.SPACING_MD)