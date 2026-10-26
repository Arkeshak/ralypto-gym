from typing import List, Dict, Set
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Ralypto Gym"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "dev-secret-key-ralypto-gym-management-2026-super-secure"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    QR_TOKEN_EXPIRE_SECONDS: int = 60
    DATABASE_URL: str = "sqlite:///./ralypto_gym.db"
    GEMINI_API_KEY: str = ""
    LLM_MODEL: str = "gemini-1.5-flash"
    VITE_DEV_TOOLS: bool = True
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["*"]

    # Plan definitions
    PLAN_FEATURES: Dict[str, Set[str]] = {
        "Basic": {
            "members",
            "plans",
            "payments",
            "checkin",
            "staff",
            "basic_reports",
        },
        "Standard": {
            "members",
            "plans",
            "payments",
            "checkin",
            "staff",
            "basic_reports",
            "classes",
            "personal_training",
            "member_app",
            "workouts",
            "progress",
            "churn_rules",
            "crowd",
        },
        "Premium": {
            "members",
            "plans",
            "payments",
            "checkin",
            "staff",
            "basic_reports",
            "classes",
            "personal_training",
            "member_app",
            "workouts",
            "progress",
            "churn_rules",
            "crowd",
            "ai_coach",
            "ai_assistant",
            "ask_gym",
            "winback_agent",
            "weekly_summary",
            "multi_branch",
        },
    }

    PLAN_MEMBER_LIMITS: Dict[str, int] = {
        "Basic": 150,
        "Standard": 500,
        "Premium": 9999999,
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
