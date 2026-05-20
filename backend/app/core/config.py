from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "COSCO GD Cockpit API"
    app_version: str = "0.1.0"
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/cosco_gd"
    )
    redis_url: str = "redis://localhost:6379/0"


settings = Settings()
