"""Media helpers: URL resolution and the shared Audio service.

The audio service keeps a module-level strong reference (``_audio_refs``).
Flet's page service registry drops services whose refcount is too low, which
used to break playback with a "Future not completed" timeout. Holding a strong
reference keeps the service alive across re-renders.
"""

from __future__ import annotations

import re
import urllib.parse

import flet as ft
from flet_audio import Audio

_audio_refs: list = []


def resolve_media_url(url: str | None, base_url: str) -> str:
    if not url:
        return url
    url = url.strip()
    # Some image services pass a "wrap" URL that contains the real image in
    # the imgurl query parameter; unwrap it so the <img> can load directly.
    if re.search(r"[?&]imgurl=", url):
        direct = (
            urllib.parse.parse_qs(urllib.parse.urlsplit(url).query).get("imgurl")
            or [None]
        )[0]
        if direct:
            url = direct
    if url.startswith(("http://", "https://")):
        return url
    return f"{base_url.rstrip('/')}/{url.lstrip('/')}"


def ensure_audio() -> Audio:
    """Return the shared Audio service, creating and registering it if needed."""
    page = ft.context.page
    if not _audio_refs:
        _audio_refs.append(Audio(src=None, volume=1.0))
    audio = _audio_refs[0]
    if audio not in page.services:
        page.services.append(audio)
    registry = page._services
    if audio not in registry._services:
        registry.register_service(audio)
    return audio


async def stop_audio() -> None:
    """Pause the shared audio when leaving a question (Play can resume it)."""
    await ensure_audio().pause()


def launch_url(url: str) -> None:
    page = ft.context.page
    page.launch_url(url)