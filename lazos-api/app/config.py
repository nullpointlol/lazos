"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Database
    DATABASE_URL: str = "sqlite:///./lazos_temp.db"

    # CORS - Read from env var with comma-separated values
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:3000"

    # JWT (for future auth implementation)
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Storage (Cloudflare R2)
    R2_ENDPOINT: str = ""
    R2_ACCESS_KEY: str = ""
    R2_SECRET_KEY: str = ""
    R2_BUCKET: str = "lazos-images"
    R2_PUBLIC_URL: str = ""

    # Application
    PROJECT_NAME: str = "LAZOS API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Admin & Moderation
    ADMIN_PASSWORD: str = ""
    MODERATOR_EMAIL: str = ""

    # Email (SMTP)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # Cloudflare Workers AI
    CLOUDFLARE_ACCOUNT_ID: str = ""
    CLOUDFLARE_R2IMAGES_API_TOKEN: str = ""
    CLOUDFLARE_WORKERSAI_API_TOKEN: str = ""
    CLOUDFLARE_AI_GATEWAY_URL: str = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into list of origins"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Create settings instance
settings = Settings()
