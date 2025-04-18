# backend/app/config.py

from pydantic_settings import BaseSettings

from app.constants import PROJECT_NAME


class Settings(BaseSettings):
    PROJECT_NAME: str = PROJECT_NAME
    LOG_LEVEL: str = "INFO"
    PYTHON_ENV: str = "dev"

    class Config:
        env_file = ".env"


settings = Settings()
