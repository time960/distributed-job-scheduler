from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgrespassword@localhost:5432/scheduler"
    redis_url: str = "redis://localhost:6379/0"
    environment: str = "development"
    worker_batch_size: int = 10
    worker_poll_interval_seconds: int = 2
    job_timeout_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
