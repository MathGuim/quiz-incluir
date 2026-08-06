from __future__ import annotations

import flet as ft
from flet import component, use_effect, use_state

import theme
from config import APP_TITLE
from controllers.quiz_controller import QuizController
from state.app_state import AppState
from widgets.feedback import notify

SECTION_ORDER = [("reading", "Reading"), ("listening", "Listening"), ("vocabulary", "Vocabulary")]

_LEVEL_COLORS = {
    "A1": ("#E8F5E9", "#2E7D32"),
    "A2": ("#E8F5E9", "#2E7D32"),
    "B1": ("#E8F0FE", "#1A73E8"),
    "B2": ("#E8F0FE", "#1A73E8"),
    "C1": ("#F3E8FF", "#7C3AED"),
    "C2": ("#F3E8FF", "#7C3AED"),
}
_LEVEL_DEFAULT_COLORS = ("#EEF2FF", "#6C63FF")


def _level_colors(level: str | None) -> tuple[str, str]:
    return _LEVEL_COLORS.get((level or "").upper(), _LEVEL_DEFAULT_COLORS)


@component
def QuizPickerScreen(state: AppState, controller: QuizController):
    quizzes, set_quizzes = use_state([])
    error, set_error = use_state("")
    loading, set_loading = use_state(True)
    query, set_query = use_state("")

    def load():
        try:
            set_quizzes(controller.list_quizzes())
            set_error("")
        except Exception as ex:
            set_error(f"Could not load quizzes: {ex}")
        finally:
            set_loading(False)

    use_effect(load, [])

    def start(quiz):
        try:
            controller.start(quiz)
            ft.context.page.navigate("/quiz/0")
        except Exception as ex:
            notify(f"Could not start quiz: {ex}", error=True)

    hero = ft.Container(
        border_radius=24,
        padding=24,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=["#6C63FF", "#8B7BFF"],
        ),
        content=ft.Column(
            [
                ft.Text(
                    "👋 Welcome back",
                    size=16,
                    color=ft.Colors.WHITE_70,
                ),
                ft.Text(
                    "Choose your next quiz",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(
                    "Keep building your language skills with short practice sessions.",
                    size=14,
                    color=ft.Colors.WHITE_70,
                ),
            ],
            spacing=6,
        ),
    )

    search = ft.TextField(
        hint_text="Search quizzes",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=16,
        filled=True,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        border_color=ft.Colors.TRANSPARENT,
        value=query,
        on_change=lambda e: set_query(e.control.value),
    )

    def _quiz_card(quiz):
        circle_bg, circle_fg = _level_colors(quiz.level)
        return ft.Card(
            elevation=2,
            margin=0,
            content=ft.Container(
                padding=20,
                border_radius=20,
                ink=True,
                on_click=lambda e, q=quiz: start(q),
                animate=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
                content=ft.Row(
                    [
                        ft.Container(
                            width=60,
                            height=60,
                            border_radius=30,
                            bgcolor=circle_bg,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Text(
                                (quiz.level or "–").upper(),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=circle_fg,
                            ),
                        ),
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(
                                            quiz.title,
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            expand=True,
                                        ),
                                        ft.Icon(
                                            ft.Icons.CHEVRON_RIGHT_ROUNDED,
                                            color=theme.MUTED,
                                        ),
                                    ]
                                ),
                                ft.Text(
                                    quiz.description
                                    or "Practice vocabulary and grammar.",
                                    size=14,
                                    color=theme.MUTED_700,
                                ),
                                ft.Container(
                                    margin=ft.Margin(top=8),
                                    padding=ft.Padding(
                                        left=10,
                                        top=6,
                                        right=10,
                                        bottom=6,
                                    ),
                                    bgcolor="#EEF2FF",
                                    border_radius=20,
                                    content=ft.Row(
                                        [
                                            ft.Icon(
                                                ft.Icons.HELP_OUTLINE,
                                                size=14,
                                                color="#6C63FF",
                                            ),
                                            ft.Text(
                                                f"{len(quiz.question_ids)} Questions",
                                                size=12,
                                                weight=ft.FontWeight.W_500,
                                                color="#6C63FF",
                                            ),
                                        ],
                                        tight=True,
                                        spacing=5,
                                    ),
                                ),
                            ],
                            spacing=6,
                            expand=True,
                        ),
                    ],
                    spacing=18,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
        )

    if loading:
        body = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                [
                    ft.ProgressRing(),
                    ft.Text(
                        "Loading quizzes...",
                        color=theme.MUTED,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
        )

    elif error:
        body = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.ERROR_OUTLINE,
                        color=theme.ERROR,
                        size=50,
                    ),
                    ft.Text(
                        error,
                        color=theme.ERROR,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
        )

    elif not quizzes:
        body = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.AUTO_STORIES_OUTLINED,
                        size=72,
                        color=theme.MUTED,
                    ),
                    ft.Text(
                        "No quizzes available",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Check back later for new learning content.",
                        color=theme.MUTED,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
        )

    else:
        term = (query or "").strip().lower()
        filtered = [
            q
            for q in quizzes
            if not term
            or term in f"{q.title} {q.description or ''}".lower()
        ]

        if not filtered:
            content = ft.Container(
                padding=ft.Padding(left=0, top=24, right=0, bottom=0),
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    [
                        ft.Icon(
                            ft.Icons.SEARCH_OFF_ROUNDED,
                            size=48,
                            color=theme.MUTED,
                        ),
                        ft.Text(
                            "No quizzes match your search",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "Try a different keyword.",
                            color=theme.MUTED,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
            )
        else:
            sections: list[ft.Control] = []
            for key, title in SECTION_ORDER:
                items = [q for q in filtered if (q.category or "").lower() == key]
                if not items:
                    continue
                sections.append(
                    ft.Text(title, size=22, weight=ft.FontWeight.BOLD)
                )
                sections.extend(_quiz_card(q) for q in items)
            content = ft.Column(sections, spacing=20)

        body = ft.Container(
            padding=20,
            expand=True,
            content=ft.Column(
                [
                    hero,
                    search,
                    content,
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            ),
        )

    return ft.View(
        route="/quizzes",
        bgcolor=ft.Colors.SURFACE,
        appbar=ft.AppBar(
            bgcolor=ft.Colors.TRANSPARENT,
            elevation=0,
            center_title=False,
            title=ft.Text(
                APP_TITLE,
                weight=ft.FontWeight.BOLD,
            ),
            actions=[
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding(right=12),
                    content=ft.CircleAvatar(
                        radius=18,
                        bgcolor="#6C63FF",
                        content=ft.Text(
                            state.email[:1].upper(),
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ),
                )
            ],
        ),
        controls=[body],
    )