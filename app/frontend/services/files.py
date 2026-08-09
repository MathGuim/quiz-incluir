"""Shared FilePicker service for saving downloaded files (e.g. PDF reports).

Registered lazily, on first actual use (``save_bytes``, called from the
results-screen download button) rather than eagerly at startup like
``services.media.register_audio``: by the time a user reaches that button the
page has been open and interacted with for a while, so there's no "before the
page is built" timing window to protect here, and eagerly registering a
second service alongside Audio at startup is an avoidable risk to Audio's own
timing-sensitive binding for a feature that isn't needed yet. The instance is
stored via ``services.page_store`` (a strong, per-page reference) rather than
a module-level global: a module global is shared by every connected browser
session in the same server process — the same bug class that made audio
started on one client's page play back on a different client's page (see
``services/media.py``) also meant the PDF "Save As" dialog could be wired to
a different, unrelated session's page instead of the one that clicked
Download.
"""

from __future__ import annotations

import flet as ft

from services.page_store import get_or_create


def register_file_picker(page: ft.Page) -> ft.FilePicker:
    picker = get_or_create(page, "file_picker", ft.FilePicker)
    if picker not in page.services:
        page.services.append(picker)
    return picker


def ensure_file_picker(page: ft.Page) -> ft.FilePicker:
    return register_file_picker(page)


async def save_bytes(file_name: str, data: bytes) -> str | None:
    picker = ensure_file_picker(ft.context.page)
    return await picker.save_file(file_name=file_name, src_bytes=data)
