from __future__ import annotations

import flet as ft
from flet import component, use_effect, use_state

import theme
from config import APP_TITLE
from controllers.quiz_controller import QuizController
from state.app_state import AppState
from widgets.feedback import notify


@component
def QuizPickerScreen(state: AppState, controller: QuizController):
    quizzes, set_quizzes = use_state([])
    error, set_error = use_state("")
    loading, set_loading = use_state(True)

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

    cards = [
        ft.Card(
            content=ft.Container(
                padding=16,
                ink=True,
                on_click=lambda e, q=quiz: start(q),
                content=ft.Column(
                    [
                        ft.Text(quiz.title, size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            quiz.description
                            or f"{len(quiz.question_ids)} questions",
                            size=13,
                            color=theme.MUTED_700,
                        ),
                        ft.Text(
                            f"{len(quiz.question_ids)} questions",
                            size=12,
                            color=theme.MUTED,
                        ),
                    ],
                    spacing=theme.SPACING_SM,
                ),
            )
        )
        for quiz in quizzes
    ]

    header = ft.Text("Choose a quiz", size=26, weight=ft.FontWeight.BOLD)
    if loading:
        body = ft.Column(
            [header, ft.ProgressRing()], spacing=12, expand=True, scroll=ft.ScrollMode.AUTO
        )
    else:
        body = ft.Column(
            [
                ft.Text(f"Hi {state.email}", size=13),
                header,
                ft.Container(height=8),
                *([] if not error else [ft.Text(error, color=theme.ERROR)]),
                *cards,
            ],
            spacing=theme.SPACING_LG,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    return ft.View(
        route="/quizzes",
        appbar=ft.AppBar(title=ft.Text("Quizzes"), center_title=True),
        controls=[body],
    )