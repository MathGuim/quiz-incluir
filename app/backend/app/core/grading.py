"""Answer grading logic for quiz questions.

Each question stores its expected answer inside ``config``:

- ``multiple_choice``: ``{"options": [...], "correct_index": n}``
  student response: ``{"selected": <option string>}``
- ``multiple_selection``: ``{"options": [...], "correct_indices": [..]}``
  student response: ``{"selected": [<option string>, ...]}``
- ``true_false``: ``{"answer": bool}``
  student response: ``{"selected": bool}``
- ``short_text``: ``{"accepted_answers": [...]}``
  student response: ``{"text": str}`` (matched trimmed + case-insensitive)
"""

from typing import Any

from app.models import Question, QuestionType


def _norm(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().lower()
    if isinstance(value, list):
        return {_norm(v) for v in value}
    return value


def grade_question(question: Question, response: dict[str, Any]) -> bool:
    config = question.config or {}
    try:
        if question.type == QuestionType.MULTIPLE_CHOICE:
            correct = config["options"][config["correct_index"]]
            return _norm(response.get("selected")) == _norm(correct)

        if question.type == QuestionType.MULTIPLE_SELECTION:
            correct = [config["options"][i] for i in config["correct_indices"]]
            return _norm(response.get("selected")) == _norm(correct)

        if question.type == QuestionType.TRUE_FALSE:
            return response.get("selected") == config.get("answer")

        if question.type == QuestionType.SHORT_TEXT:
            text = _norm(response.get("text"))
            accepted = [_norm(a) for a in config.get("accepted_answers", [])]
            return text in accepted
    except (KeyError, IndexError, TypeError):
        return False

    return False
