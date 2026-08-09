from __future__ import annotations

import flet as ft
from flet import component

import theme
from config import APP_TITLE
from controllers.quiz_controller import QuizController
from services.files import save_bytes
from state.app_state import AppState
from widgets.feedback import notify


@component
def ResultsScreen(state: AppState, controller: QuizController):
    result = state.result
    score = (result.score or 0) if result else 0
    max_score = (result.max_score or 0) if result else 0
    pct = round(100 * score / max_score, 1) if max_score else 0.0
    passed = pct >= 50

    def again(e):
        ft.context.page.navigate("/quizzes")

    async def download_pdf(e):
        try:
            pdf_bytes = await controller.download_report()
            await save_bytes(f"quiz-report-{state.attempt_id}.pdf", pdf_bytes)
        except Exception as ex:
            notify(f"Could not download report: {ex}", error=True)

    body = ft.Column(
        [
            ft.Container(height=12),
            ft.Icon(
                ft.Icons.EMOJI_EVENTS if passed else ft.Icons.SENTIMENT_NEUTRAL,
                size=64,
                color=ft.Colors.AMBER_600 if passed else ft.Colors.GREY_500,
            ),
            ft.Text(
                "Quiz completed!",
                size=26,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=8),
            ft.Text(
                f"{score:g} / {max_score:g}",
                size=44,
                weight=ft.FontWeight.BOLD,
                color=theme.PRIMARY,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(
                f"{pct}% correct",
                size=16,
                color=theme.MUTED_700,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=24),
            ft.FilledButton("Take another quiz", on_click=again, expand=True),
            ft.Container(height=8),
            ft.OutlinedButton(
                "Download PDF",
                icon=ft.Icons.PICTURE_AS_PDF,
                on_click=download_pdf,
                expand=True,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    return ft.View(
        route="/results",
        appbar=ft.AppBar(title=ft.Text("Results"), center_title=True),
        controls=[body],
    )