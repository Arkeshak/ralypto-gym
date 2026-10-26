from datetime import datetime
from typing import Optional
from sqlmodel import Field
from app.models.base import BaseUUIDModel, utc_now


class ChurnScore(BaseUUIDModel, table=True):
    __tablename__ = "churn_scores"

    member_id: str = Field(nullable=False, index=True)
    score: int = Field(default=0, index=True)  # 0-100
    level: str = Field(default="Low")  # High (60+), Medium (30-59), Low (<30)
    reasons_json: str = Field(default="[]")
    computed_at: datetime = Field(default_factory=utc_now)


class AIAction(BaseUUIDModel, table=True):
    __tablename__ = "ai_actions"

    user_id: Optional[str] = Field(default=None, index=True)
    feature: str = Field(nullable=False, index=True)  # churn, coach, assistant, crowd, ask_gym, weekly_summary
    tool: Optional[str] = None
    input_json: str = Field(default="{}")
    output_json: str = Field(default="{}")
    status: str = Field(default="completed")  # completed, failed, pending_confirmation
    cost_estimate: float = Field(default=0.0)
