from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Job Hunter"
    debug: bool = True
    secret_key: str = "dev-secret-change-in-production"
    access_token_expire_minutes: int = 60 * 24 * 7
    algorithm: str = "HS256"

    database_url: str = "sqlite+aiosqlite:///./ai_job_hunter.db"
    upload_dir: str = "uploads"
    max_cv_size_mb: int = 10

    ai_provider: str = "openai"
    ai_api_key: str = ""
    ai_base_url: str = "https://api.openai.com/v1"
    ai_model: str = "gpt-4o-mini"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "noreply@aijobhunter.local"

    frontend_url: str = "http://localhost:5173"

    match_weight_skills: float = 0.35
    match_weight_experience: float = 0.20
    match_weight_role: float = 0.20
    match_weight_location: float = 0.10
    match_weight_education: float = 0.05
    match_weight_technology: float = 0.05
    match_weight_preference: float = 0.05

    default_search_interval_hours: int = 6

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def max_cv_bytes(self) -> int:
        return self.max_cv_size_mb * 1024 * 1024

    def match_weights(self) -> dict[str, float]:
        return {
            "skills": self.match_weight_skills,
            "experience": self.match_weight_experience,
            "role": self.match_weight_role,
            "location": self.match_weight_location,
            "education": self.match_weight_education,
            "technology": self.match_weight_technology,
            "preference": self.match_weight_preference,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
