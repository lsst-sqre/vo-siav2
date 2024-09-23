"""Data collection models."""

from dataclasses import dataclass


@dataclass
class DataCollection:
    """Model to represent a Butler collection."""

    config: str | None = None
    label: str | None = None
    repository: str | None = None
    default: bool = False
