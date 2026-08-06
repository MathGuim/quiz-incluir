"""Entrypoint: configure the page and render the declarative app tree."""

from __future__ import annotations

import flet as ft

import config
from controllers.auth_controller import AuthController
from controllers.quiz_controller import QuizController
from router import make_app
from services.api import QuizApiClient
from state.app_state import AppState


def main(page: ft.Page) -> None:
    page.title = config.APP_TITLE
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 24
    page.appbar = ft.AppBar(title=ft.Text(config.APP_TITLE), center_title=True)

    try:
        page.window.width = 520
        page.window.height = 820
    except Exception:
        pass

    state = AppState()
    api = QuizApiClient(config.API_URL)
    auth = AuthController(state, api)
    quiz_controller = QuizController(state, api)

    page.render_views(make_app(state, auth, quiz_controller))


if __name__ == "__main__":
    ft.run(main)