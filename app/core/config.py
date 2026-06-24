# config.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database connection URL loaded from environment or .env file
    secret_key: str = Field(default=..., alias="SECRET_KEY")
    db_url: str = Field(default=..., alias="DATABASE_URL")
    project_url: str = Field(default=...,alias="PROJECT_URL")
    algorithm: str = Field(default=...,alias="ALGORITHM")
    token_expire_minutes: int = Field(default=...,alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    version: str = Field(default=...,alias="VERSION")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

settings = Settings()



