"""Media model matching backend MediaRead + MediaType enum."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class MediaType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class Media(BaseModel):
    id: str
    type: MediaType
    url: str | None = None
    caption: str | None = None
    position: int = 0