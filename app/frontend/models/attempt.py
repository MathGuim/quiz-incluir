"""Auth and attempt models: re-exports the shared read-schemas.

See ``quiz_shared.schemas`` for the field lists (``TokenRead``, ``UserRead``,
``AttemptRead``).
"""

from __future__ import annotations

from quiz_shared.schemas import AttemptRead as Attempt
from quiz_shared.schemas import AttemptRead as AttemptResult
from quiz_shared.schemas import TokenRead as Token
from quiz_shared.schemas import UserRead as User

__all__ = ["Token", "User", "Attempt", "AttemptResult"]
