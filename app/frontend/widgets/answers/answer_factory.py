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


class MultipleChoice(AnswerWidget):
    def __init__(self, options: list[str]):
        self.options = options

    def build(self, previous: dict | None) -> ft.Control:
        group = ft.RadioGroup(
            content=ft.Column(
                [ft.Radio(value=opt, label=opt, expand=True) for opt in self.options],
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
        checkboxes = [ft.Checkbox(label=opt, expand=True) for opt in self.options]
        if previous:
            selected = previous.get("selected") or []
            for cb in checkboxes:
                cb.value = cb.label in selected
        column = ft.Column(controls=checkboxes, spacing=4)
        column.data = checkboxes
        self.control = column
        return column

    def extract(self) -> dict | None:
        selected = [cb.label for cb in self.control.data if cb.value]
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