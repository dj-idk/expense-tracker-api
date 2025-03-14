from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dotenv import load_dotenv
from functools import lru_cache


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    TOKEN_COOKIE_NAME: str = "Authorization"
    CSRF_TOKEN_SECRET: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings():
    load_dotenv(override=True)
    settings = Settings()
    return settings


settings = get_settings()
