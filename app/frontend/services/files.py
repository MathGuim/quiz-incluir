"""Shared FilePicker service for saving downloaded files (e.g. PDF reports).

Registered lazily, on first actual use (``save_bytes``, called from the
results-screen download button) rather than eagerly at startup like
``services.media.register_audio``: by the time a user reaches that button the
page has been open and interacted with for a while, so there's no "before the
page is built" timing window to protect here, and eagerly registering a
second service alongside Audio at startup is an avoidable risk to Audio's own
timing-sensitive binding for a feature that isn't needed yet. A module-level
strong reference keeps it alive across re-renders once registered.
"""

from __future__ import annotations

import flet as ft

_file_picker: ft.FilePicker | None = None


def register_file_picker(page: ft.Page) -> ft.FilePicker:
    global _file_picker
    if _file_picker is None:
        _file_picker = ft.FilePicker()
    if _file_picker not in page.services:
        page.services.append(_file_picker)
    return _file_picker


def ensure_file_picker(page: ft.Page) -> ft.FilePicker:
    return register_file_picker(page)


async def save_bytes(file_name: str, data: bytes) -> str | None:
    picker = ensure_file_picker(ft.context.page)
    return await picker.save_file(file_name=file_name, src_bytes=data)
