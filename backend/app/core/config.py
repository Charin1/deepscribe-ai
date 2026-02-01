"""Core configuration for DeepScribe AI Backend."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),  # Check backend/.env first, then root/.env
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API Keys
    groq_api_key: str = ""
    serper_api_key: str = ""
    tavily_api_key: str = ""
    openai_api_key: str = ""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/deepscribe"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
