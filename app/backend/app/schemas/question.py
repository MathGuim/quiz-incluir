from typing import Any

from pydantic import ValidationError, field_validator, model_validator
from sqlmodel import SQLModel

from app.core.question_types import HANDLERS
from app.models import QuestionType
from quiz_shared.schemas import QuestionRead

__all__ = ["QuestionBase", "QuestionCreate", "QuestionUpdate", "QuestionRead"]


def _validate_config(question_type: QuestionType, config: dict[str, Any]) -> None:
    handler = HANDLERS.get(question_type)
    if handler is None:
        return
    try:
        handler.config_model.model_validate(config)
    except ValidationError as exc:
        raise ValueError(f"config does not match {question_type.value} shape: {exc}") from exc


class QuestionBase(SQLModel):
    type: QuestionType
    prompt: str
    suggested_score: float = 1.0
    config: dict[str, Any] = {}


class QuestionCreate(QuestionBase):
    @field_validator("config", mode="before")
    @classmethod
    def ensure_config_dict(cls, v: Any) -> dict[str, Any]:
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError("config must be an object")
        return v

    @model_validator(mode="after")
    def check_config_shape(self) -> "QuestionCreate":
        _validate_config(self.type, self.config)
        return self


class QuestionUpdate(SQLModel):
    type: QuestionType | None = None
    prompt: str | None = None
    suggested_score: float | None = None
    config: dict[str, Any] | None = None

    @model_validator(mode="after")
    def check_config_shape(self) -> "QuestionUpdate":
        # Only checkable when both fields are present in the same partial
        # update — validating a lone `config` change against the question's
        # existing (unknown here) type would need a DB lookup.
        if self.type is not None and self.config is not None:
            _validate_config(self.type, self.config)
        return self
