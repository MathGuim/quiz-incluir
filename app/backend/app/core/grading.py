"""Answer grading for quiz questions.

Per-type config/response shapes and grading rules live in
:mod:`app.core.question_types`; this module wires an attempt's response to
the matching handler.
"""

from typing import Any

from app.core.question_types import HANDLERS, parse_config
from app.models import Question


def grade_question(question: Question, response: dict[str, Any]) -> bool:
    handler = HANDLERS.get(question.type)
    if handler is None:
        return False
    config = parse_config(question)
    if config is None:
        return False
    return handler.grade(config, response)
