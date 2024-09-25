"""Configuration definition."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from safir.logging import LogLevel, Profile

from .models.data_collections import DataCollection
from .models.query_engines import QueryEngines

__all__ = ["Config", "config"]


class Config(BaseSettings):
    """Configuration for vo-siav2."""

    name: str = Field("vo-siav2", title="Name of application")
    """Name of application."""

    path_prefix: str = Field("/api/images", title="URL prefix for application")
    """URL prefix for application."""

    profile: Profile = Field(
        Profile.development, title="Application logging profile"
    )
    """Application logging profile."""

    log_level: LogLevel = Field(
        LogLevel.INFO, title="Log level of the application's logger"
    )
    """Log level of the application's logger."""

    model_config = SettingsConfigDict(
        env_prefix="SIAV2_", case_sensitive=False
    )
    """Configuration for the model settings."""

    query_engine: QueryEngines = QueryEngines.REMOTE_BUTLER
    """Configuration for the query engine."""

    data_collections: Annotated[
        list[DataCollection],
        Field(title="Data collections"),
    ] = []
    """Configuration for the query engine."""

    slack_webhook: Annotated[
        HttpUrl | None, Field(title="Slack webhook for exception reporting")
    ] = None
    """Slack webhook for exception reporting."""


config = Config()
"""Configuration instance for vo-siav2."""
