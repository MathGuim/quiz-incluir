from __future__ import annotations

import flet as ft
from flet import component, use_ref

import theme
from config import APP_TITLE
from controllers.quiz_controller import QuizController
from state.app_state import AppState
from widgets.answers.answer_factory import AnswerWidget, answer_factory
from services.media import stop_audio
from widgets.feedback import notify
from widgets.progress_indicator import build_progress
from widgets.question_card import question_card


@component
def QuestionScreen(state: AppState, controller: QuizController):
    answer_ref = use_ref(None)

    question = state.current_question
    if question is None:
        return ft.View(
            route="/quiz",
            appbar=ft.AppBar(title=ft.Text(APP_TITLE), center_title=True),
            controls=[ft.Text("No question to display.")],
        )

    idx = state.current_index
    total = state.total
    is_last = idx >= total - 1

    widget: AnswerWidget = answer_factory(question)
    widget.build(state.answers.get(idx))
    answer_ref.current = widget

    async def on_back(e):
        await stop_audio()
        controller.previous()

    async def on_submit(e):
        print("NEXT CLICKED", flush=True)
        await stop_audio()
        response = widget.extract()
        if response is None:
            notify("Please answer the question first.", error=True)
            return
        try:
            controller.submit(question.id, response)
        except Exception as ex:
            notify(f"Could not save your answer: {ex}", error=True)
            return
        if state.finished:
            ft.context.page.navigate("/results")

    back_btn = ft.OutlinedButton(
        "Back",
        icon=ft.Icons.ARROW_BACK,
        on_click=on_back,
        disabled=idx == 0,
        expand=True,
    )
    next_btn = ft.FilledButton(
        "Finish" if is_last else "Next",
        icon=ft.Icons.CHECK if is_last else ft.Icons.ARROW_FORWARD,
        on_click=on_submit,
        expand=True,
    )

    body = ft.Column(
        [
            build_progress(total, state.answers, idx),
            ft.Container(height=12),
            question_card(question),
            ft.Container(height=8),
            widget.control,
            ft.Row([back_btn, next_btn], spacing=theme.SPACING_LG),
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    return ft.View(
        route=f"/quiz/{idx}",
        appbar=ft.AppBar(
            title=ft.Text(f"Question {idx + 1} of {total}"), center_title=True
        ),
        controls=[body],
    )