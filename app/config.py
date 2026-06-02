from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+pysqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/0"
    service_name: str = "ai-job-orchestrator"
    embedding_provider: str = "fake"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
