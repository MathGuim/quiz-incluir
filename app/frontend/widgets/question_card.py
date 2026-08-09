"""Question card: renders the prompt plus its media blocks."""

from __future__ import annotations

import flet as ft

from models.question import Question
from widgets.media import media_area
import config
import theme


def question_card(question: Question) -> ft.Control:
    return theme.card(
        padding=20,
        content=ft.Column(
            [
                ft.Text(
                    question.prompt,
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=theme.TEXT_PRIMARY,
                ),
                *media_area(question.media, config.API_URL),
            ],
            spacing=theme.SPACING_LG,
        ),
    )