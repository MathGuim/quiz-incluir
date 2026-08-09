"""Media model: re-exports the shared enum/read-schema.

See ``quiz_shared.schemas.MediaRead`` for the field list.
"""

from __future__ import annotations

from quiz_shared.enums import MediaType
from quiz_shared.schemas import MediaRead as Media

__all__ = ["MediaType", "Media"]
