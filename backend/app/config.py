from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://attendance:attendance@localhost:5432/attendance"
    jwt_secret: str = "change-me-in-production-use-long-random-string"
    jwt_expire_minutes: int = 480
    jwt_algorithm: str = "HS256"
    admin_default_login: str = "admin"
    admin_default_password: str = "admin"
    cors_origins: str = "http://localhost:8080,http://localhost:5173"
    apk_download_url: str = "/apk/attendance-placeholder.apk"
    signature_max_age_seconds: int = 30

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
