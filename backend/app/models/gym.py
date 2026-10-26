from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import SQLModel, Field
from app.models.base import BaseUUIDModel, utc_now


class Gym(SQLModel, table=True):
    __tablename__ = "gyms"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
        nullable=False
    )
    name: str = Field(nullable=False, index=True)
    code: str = Field(default="IPF", index=True)
    logo_url: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    plan: str = Field(default="Premium")  # Basic, Standard, Premium
    plan_status: str = Field(default="active")  # active, past_due, canceled
    plan_renews_at: Optional[datetime] = None
    timezone: str = Field(default="Asia/Colombo")
    currency: str = Field(default="LKR")
    settings_json: str = Field(default="{}")
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)


class GymSettings(BaseUUIDModel, table=True):
    __tablename__ = "gym_settings"

    grace_days: int = Field(default=7)
    late_cancel_hours: int = Field(default=2)
    auto_checkout_hours: int = Field(default=3)
    receipt_header: str = Field(default="Iron Peak Fitness - Colombo")
    receipt_footer: str = Field(default="Thank you for training with us! No pain no gain.")
    settings_json: str = Field(default="{}")
