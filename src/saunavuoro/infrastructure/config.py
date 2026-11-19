import os
from dataclasses import dataclass

from dotenv import load_dotenv

DEFAULT_DATABASE_URL = "postgresql+psycopg://saunavuoro:saunavuoro@localhost:5432/saunavuoro"


@dataclass(frozen=True)
class Settings:
    database_url: str


def load_settings() -> Settings:
    load_dotenv()
    return Settings(database_url=os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL))
