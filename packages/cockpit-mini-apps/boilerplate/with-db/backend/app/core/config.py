from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "{{PROJECT_NAME_TITLE}}"
    APP_VERSION: str = "0.1.0"
    DATABASE_URL: str = "postgresql+asyncpg://miniapp:miniapp@db:5432/miniapp"
    DEBUG: bool = False
    # "pretty" para dev (colorido), "json" para produção
    LOG_FORMAT: str = "pretty"


settings = Settings()
