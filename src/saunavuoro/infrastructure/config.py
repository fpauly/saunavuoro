"""Application configuration loaded from environment variables and .env."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "SaunaVuoro"
    environment: Literal["development", "test", "production"] = "development"
    log_level: str = "info"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://saunavuoro:saunavuoro@localhost:5434/saunavuoro"


@lru_cache
def get_settings() -> Settings:
    return Settings()
