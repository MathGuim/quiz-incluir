"""Media widgets: one viewer per media type, plus a factory.

Image/text/video viewers are plain declarative controls; audio drives the
shared Audio service via side-effect handlers.
"""

from __future__ import annotations

import flet as ft
from flet import component, use_effect, use_ref, use_state

from flet_video import Video, VideoMedia

from models.media import Media, MediaType
from services.media import ensure_audio, launch_url, resolve_media_url
import theme


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
        audio = ensure_audio()
        audio.src = resolved_url
        audio.on_duration_change = on_duration
        audio.on_position_change = on_position

    use_effect(attach, [resolved_url])

    async def play(e):
        audio = ensure_audio()
        attach()
        ft.context.page.update()
        await audio.play()

    async def pause(e):
        await ensure_audio().pause()

    async def resume(e):
        await ensure_audio().resume()

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
        widgets.append(
            ft.Markdown(
                caption or url,
                selectable=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            )
        )
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