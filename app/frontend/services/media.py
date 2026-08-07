"""Media helpers: URL resolution and the shared Audio service.

The Audio service is created once, with a concrete ``src``, and registered
into ``page.services`` *before* the page is built/rendered. flet binds a
client-side invoke-method listener for a service when it is added to the page —
registering late/after page open (or without a ``src``) is what caused
``Timeout waiting for invoke method listener`` errors (see the flet 0.86.4
changelog). A module-level strong reference keeps the service alive across
re-renders, because flet drops weakly-referenced services from the registry.
"""

from __future__ import annotations

import re
import urllib.parse

import flet as ft
from flet_audio import Audio

# A valid placeholder source, so the service satisfies the "src must be a
# string" contract at construction. It is replaced with a real URL whenever a
# question's audio player attaches.
PLACEHOLDER_SRC = "https://storage.googleapis.com/quiz_public_bucket/LE_listening_C1_Birthday_parties.mp3"

_audio: Audio | None = None


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


def register_audio(page: ft.Page, src: str = PLACEHOLDER_SRC) -> Audio:
    """Create (once) and register the shared Audio service on the page.

    Call this before the page is rendered so the web client binds the
    invoke-method handler for the audio service. Idempotent.
    """
    global _audio
    if _audio is None:
        _audio = Audio(src=src, volume=1.0)
    if _audio not in page.services:
        page.services.append(_audio)
    return _audio


def ensure_audio(page: ft.Page) -> Audio:
    """Return the shared Audio service, registering it if needed."""
    return register_audio(page)


def set_audio_src(page: ft.Page, resolved_url: str) -> Audio:
    """Point the shared service at ``resolved_url`` and refresh the client."""
    audio = ensure_audio(page)
    if audio.src != resolved_url:
        audio.src = resolved_url
        audio.update()
    return audio


async def stop_audio() -> None:
    """Pause the shared audio when leaving a question (Play can resume it)."""
    if _audio is not None:
        await _audio.pause()


def launch_url(url: str) -> None:
    page = ft.context.page
    page.launch_url(url)