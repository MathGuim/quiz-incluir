"""Media widgets: one viewer per media type, plus a factory.

Image/text/video viewers are plain declarative controls; audio drives the
shared Audio service via side-effect handlers.
"""

from __future__ import annotations

import httpx
import flet as ft
from flet import component, use_effect, use_ref, use_state

from flet_video import Video, VideoMedia

from models.media import Media, MediaType
from services.media import launch_url, resolve_media_url, set_audio_src
from widgets.feedback import notify
import theme


@component
def MarkdownMedia(media: Media, base_url: str):
    """Fetch and render a TEXT media url's markdown content.

    The ``url`` points to a markdown file, so it is fetched (server-side via
    httpx) and its body is rendered through ``ft.Markdown``. If there is no url
    or the fetch fails, the caption is shown instead.
    """
    content, set_content = use_state("")
    url = media.url or ""
    caption = media.caption or ""

    def fetch():
        if not url:
            return
        try:
            resp = httpx.get(
                resolve_media_url(url, base_url),
                timeout=15,
                follow_redirects=True,
            )
            resp.raise_for_status()
            set_content(resp.text)
        except Exception:
            set_content(caption)

    use_effect(fetch, [url])

    return ft.Markdown(
        content or caption,
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
    )


@component
def AudioPlayer(resolved_url: str):
    """Declarative audio player: progress bar re-renders from hook state.

    Controls returned by a component are frozen, so the progress value is never
    mutated directly; it comes from ``use_state`` and the component re-renders.
    """
    value, set_value = use_state(0.0)
    duration_ref = use_ref(0)

    def on_duration(e):
        duration_ref.current = e.duration.in_milliseconds or 0

    def on_position(e):
        duration = duration_ref.current
        set_value(e.position / duration if duration and duration > 0 else 0.0)

    def attach():
        # The service is pre-registered (see main.py). Point it at this
        # question's source and wire position events; the web client already
        # has a bound invoke-method handler for it.
        audio = set_audio_src(ft.context.page, resolved_url)
        audio.on_duration_change = on_duration
        audio.on_position_change = on_position

    use_effect(attach, [resolved_url])

    async def play(e):
        print("PLAY CLICKED", flush=True)
        audio = set_audio_src(ft.context.page, resolved_url)
        print("AUDIO SRC SET", audio.src, flush=True)
        try:
            await audio.play()
            print("AUDIO PLAY RETURNED", flush=True)
        except Exception as ex:
            print("AUDIO PLAY FAILED", repr(ex), flush=True)
            notify(f"Could not play audio: {ex}", error=True)

    async def pause(e):
        try:
            await set_audio_src(ft.context.page, resolved_url).pause()
        except Exception as ex:
            notify(f"Could not pause audio: {ex}", error=True)

    async def resume(e):
        try:
            await set_audio_src(ft.context.page, resolved_url).resume()
        except Exception as ex:
            notify(f"Could not resume audio: {ex}", error=True)

    controls = ft.Row(
        [
            ft.TextButton("Play", icon=ft.Icons.PLAY_ARROW, on_click=play),
            ft.TextButton("Pause", icon=ft.Icons.PAUSE, on_click=pause),
            ft.TextButton("Resume", icon=ft.Icons.REPLAY, on_click=resume),
        ],
        spacing=theme.SPACING_SM,
    )
    return ft.Column([controls, ft.ProgressBar(value=value)], spacing=4)


def _build_media(media: Media, base_url: str) -> list[ft.Control]:
    """Build the flet controls for a single media item."""
    mtype = media.type
    url = media.url or ""
    caption = media.caption or ""
    widgets: list[ft.Control] = []

    if mtype == MediaType.IMAGE and url:
        resolved = resolve_media_url(url, base_url)
        widgets.append(
            ft.Image(
                src=resolved,
                height=180,
                fit=ft.BoxFit.CONTAIN,
                border_radius=theme.CARD_RADIUS,
                error_content=ft.Text(
                    caption or "Media unavailable",
                    color=ft.Colors.GREY_500,
                    italic=True,
                ),
            )
        )
    elif mtype == MediaType.TEXT and (caption or url):
        widgets.append(MarkdownMedia(media, base_url))
    elif mtype == MediaType.AUDIO and url:
        widgets.append(AudioPlayer(resolve_media_url(url, base_url)))
    elif mtype == MediaType.VIDEO and url:
        widgets.append(
            Video(
                playlist=[VideoMedia(resource=resolve_media_url(url, base_url))],
                fit=ft.BoxFit.CONTAIN,
                aspect_ratio=16 / 9,
            )
        )
    elif url:
        widgets.append(
            ft.TextButton(
                f"Open media: {url}",
                icon=ft.Icons.OPEN_IN_NEW,
                on_click=lambda e, u=resolve_media_url(url, base_url): launch_url(u),
            )
        )

    if widgets and caption and mtype != MediaType.TEXT:
        widgets.append(ft.Text(caption, size=12, color=ft.Colors.GREY_600))

    if not widgets:
        return []

    wrapped = ft.Container(
        content=ft.Column(widgets, spacing=theme.SPACING_SM),
        padding=8,
        border_radius=theme.CARD_RADIUS,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE_GREY_100),
    )
    return [wrapped]


def media_area(medias: list[Media], base_url: str) -> list[ft.Control]:
    """Build all media blocks for a question, ordered by ``position``."""
    controls: list[ft.Control] = []
    for media in sorted(medias, key=lambda media: media.position):
        controls.extend(_build_media(media, base_url))
    return controls