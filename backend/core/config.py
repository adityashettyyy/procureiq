from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str = "change-me"

    # TinyFish
    tinyfish_api_key: str
    tinyfish_base_url: str = "https://api.tinyfish.io/v1"

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"  # Faster and cheaper for extraction
    openai_max_tokens: int = 1000

    # Database
    database_url: str = "sqlite+aiosqlite:///./procureiq.db"

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Demo mode
    demo_mode: bool = False
    demo_job_delay_seconds: int = 3

    # Agent config
    agent_timeout_seconds: int = 45
    agent_max_retries: int = 1
    max_parallel_agents: int = 3

    # Business logic
    human_benchmark_minutes: int = 150
    human_hourly_rate_usd: float = 25.0

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
