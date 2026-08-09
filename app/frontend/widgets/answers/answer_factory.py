"""Answer input widgets (Strategy pattern).

Each widget builds the flet control for its question type and knows how to
extract the user's response as the JSON the backend expects.
"""

from __future__ import annotations

import flet as ft

import theme
from models.question import Question, QuestionType


class AnswerWidget:
    control: ft.Control | None = None

    def build(self, previous: dict | None) -> ft.Control:
        raise NotImplementedError

    def extract(self) -> dict | None:
        raise NotImplementedError


def _option_row(input_control: ft.Control, text: str, on_click) -> ft.Row:
    """A radio/checkbox + its label as a wrapping ``Text``.

    Flet's built-in ``Radio``/``Checkbox`` ``label=`` text does not wrap
    within the control's own width, so long options got cut off on narrow
    screens. Rendering the label as a separate ``Text`` inside an
    ``expand=True`` container gives it a bounded width to wrap against.
    The input control and the clickable text are siblings (not nested), so
    a tap on either fires exactly one handler — no double-toggle risk.
    """
    return ft.Row(
        [
            input_control,
            ft.Container(
                expand=True,
                ink=True,
                border_radius=theme.INPUT_RADIUS,
                padding=ft.Padding(left=4, top=6, right=4, bottom=6),
                on_click=on_click,
                content=ft.Text(text),
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


class MultipleChoice(AnswerWidget):
    def __init__(self, options: list[str]):
        self.options = options

    def build(self, previous: dict | None) -> ft.Control:
        group = ft.RadioGroup(content=ft.Column())

        def select(opt: str):
            def handler(e):
                group.value = opt
                group.update()

            return handler

        group.content = ft.Column(
            [
                _option_row(ft.Radio(value=opt), opt, select(opt))
                for opt in self.options
            ],
            spacing=4,
        )
        if previous and previous.get("selected"):
            group.value = previous["selected"]
        self.control = group
        return group

    def extract(self) -> dict | None:
        if self.control.value:
            return {"selected": self.control.value}
        return None


class MultiSelect(AnswerWidget):
    def __init__(self, options: list[str]):
        self.options = options

    def build(self, previous: dict | None) -> ft.Control:
        selected_prev = set((previous or {}).get("selected") or [])
        checkboxes = [
            ft.Checkbox(value=opt in selected_prev, data=opt) for opt in self.options
        ]

        def toggle(cb: ft.Checkbox):
            def handler(e):
                cb.value = not cb.value
                cb.update()

            return handler

        rows = [
            _option_row(cb, opt, toggle(cb))
            for cb, opt in zip(checkboxes, self.options)
        ]
        column = ft.Column(rows, spacing=4)
        column.data = checkboxes
        self.control = column
        return column

    def extract(self) -> dict | None:
        selected = [cb.data for cb in self.control.data if cb.value]
        if selected:
            return {"selected": selected}
        return None


class TrueFalse(AnswerWidget):
    def build(self, previous: dict | None) -> ft.Control:
        group = ft.RadioGroup(
            content=ft.Row(
                [
                    ft.Radio(value="true", label="True"),
                    ft.Radio(value="false", label="False"),
                ],
                spacing=12,
            )
        )
        if previous:
            group.value = "true" if previous.get("selected") else "false"
        self.control = group
        return group

    def extract(self) -> dict | None:
        if self.control.value:
            return {"selected": self.control.value == "true"}
        return None


class ShortText(AnswerWidget):
    def build(self, previous: dict | None) -> ft.Control:
        field = ft.TextField(
            value=(previous or {}).get("text", ""),
            label="Your answer",
            expand=True,
        )
        self.control = field
        return field

    def extract(self) -> dict | None:
        text = (self.control.value or "").strip()
        if text:
            return {"text": text}
        return None


class Unsupported(AnswerWidget):
    def build(self, previous: dict | None) -> ft.Control:
        self.control = ft.Text(
            "Unsupported question type.", color=theme.ERROR
        )
        return self.control

    def extract(self) -> dict | None:
        return None


def answer_factory(question: Question) -> AnswerWidget:
    qtype = question.type
    if qtype == QuestionType.MULTIPLE_CHOICE:
        return MultipleChoice(question.options)
    if qtype == QuestionType.MULTIPLE_SELECTION:
        return MultiSelect(question.options)
    if qtype == QuestionType.TRUE_FALSE:
        return TrueFalse()
    if qtype == QuestionType.SHORT_TEXT:
        return ShortText()
    return Unsupported()