# app/config.py

from pydantic_settings import BaseSettings

from app.constants import PROJECT_NAME


class Settings(BaseSettings):
    PROJECT_NAME: str = PROJECT_NAME
    LOG_LEVEL: str = "INFO"
    PYTHON_ENV: str = "dev"
    SUPABASE_JWT_SECRET: str
    SUPABASE_JWT_AUDIENCE: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_STORAGE_BUCKET: str

    class Config:
        env_file = ".env"


settings = Settings()
