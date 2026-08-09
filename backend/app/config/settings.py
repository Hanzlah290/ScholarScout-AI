from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from the .env file."""

    DATABASE_URL: str
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    RAW_STORAGE_PATH: str = "storage/raw_pages"
    CRAWL_MAX_PAGES: int = 50
    CRAWL_MAX_DEPTH: int = 2
    CRAWL_TIMEOUT_MS: int = 30_000

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
