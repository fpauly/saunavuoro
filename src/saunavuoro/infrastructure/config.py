import os
from dataclasses import dataclass

DEFAULT_DATABASE_URL = "postgresql+psycopg://saunavuoro:saunavuoro@localhost:5432/saunavuoro"


@dataclass(frozen=True)
class Settings:
    database_url: str


def load_settings() -> Settings:
    return Settings(database_url=os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL))
