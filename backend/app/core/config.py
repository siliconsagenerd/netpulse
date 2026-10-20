from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "NetPulse"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///./netpulse.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    auto_create_tables: bool = False

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


def get_db_url():
    return get_settings().database_url
