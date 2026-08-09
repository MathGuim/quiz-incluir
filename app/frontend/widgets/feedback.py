"""Transient UI feedback (snackbar/error toasts)."""

from __future__ import annotations

import flet as ft

import theme


def notify(message: str, error: bool = False) -> None:
    """Show a snackbar. Appends to the overlay with ``open=True`` (no Page.open)."""
    color = theme.ERROR if error else theme.SUCCESS
    snack = ft.SnackBar(
        ft.Text(message, color=ft.Colors.WHITE),
        bgcolor=color,
        open=True,
    )
    page = ft.context.page
    page.overlay.append(snack)
    page.update()