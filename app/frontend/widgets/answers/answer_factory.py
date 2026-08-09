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


def _option_row(input_control: ft.Control, text: str) -> ft.Row:
    """A radio/checkbox with its label rendered as a separate wrapping ``Text``.

    Flet's built-in ``Radio``/``Checkbox`` ``label=`` text does not wrap
    within the control's own width, so long options got cut off on narrow
    screens. Rendering the label as a plain ``Text`` inside an
    ``expand=True`` container gives it a bounded width to wrap against.

    The tap target stays the radio/checkbox itself (its native, purely
    client-side click handling — no Python round trip). A component's
    entire returned control tree is marked frozen by flet as soon as it
    renders (see ``flet/components/component.py``), so any handler here
    that mutated a captured control and called ``.update()`` on it would
    work only until the next re-render, then raise "Frozen control cannot
    be updated." — which is exactly what an earlier version of this file
    did for a "tap anywhere on the row" affordance. Not worth the
    reliability cost for a slightly bigger tap target.
    """
    return ft.Row(
        [input_control, ft.Container(expand=True, content=ft.Text(text))],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


class MultipleChoice(AnswerWidget):
    def __init__(self, options: list[str]):
        self.options = options

    def build(self, previous: dict | None) -> ft.Control:
        group = ft.RadioGroup(
            content=ft.Column(
                [_option_row(ft.Radio(value=opt), opt) for opt in self.options],
                spacing=4,
            )
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
        column = ft.Column(
            [_option_row(cb, opt) for cb, opt in zip(checkboxes, self.options)],
            spacing=4,
        )
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