"""Quiz model: re-exports the shared read-schema.

See ``quiz_shared.schemas.QuizRead`` for the field list.
"""

from __future__ import annotations

from quiz_shared.schemas import QuizRead as Quiz

__all__ = ["Quiz"]
