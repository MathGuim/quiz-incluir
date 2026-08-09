"""Per-page keyed storage for session-scoped singletons (Audio, FilePicker, ...).

``page.data`` is a single generic slot, but multiple independent services
each need their own strong, per-session reference (a module-level global is
shared by every connected browser session in the same server process, which
is what caused audio/file-download bugs where one client's action affected a
different client's page — see ``services/media.py``/``services/files.py``).
Storing a small dict on ``page.data`` lets each service keep its own key
without overwriting another service's reference.
"""

from __future__ import annotations

from typing import Callable, TypeVar

import flet as ft

T = TypeVar("T")


def get_or_create(page: ft.Page, key: str, factory: Callable[[], T]) -> T:
    store = page.data
    if store is None:
        store = {}
        page.data = store
    if key not in store:
        store[key] = factory()
    return store[key]
