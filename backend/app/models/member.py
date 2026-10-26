from datetime import datetime
from typing import Optional
from sqlmodel import Field
from app.models.base import BaseUUIDModel, utc_now


class Member(BaseUUIDModel, table=True):
    __tablename__ = "members"

    member_code: str = Field(nullable=False, index=True)
    name: str = Field(nullable=False, index=True)
    phone: str = Field(nullable=False, index=True)
    email: Optional[str] = Field(default=None, index=True)
    gender: Optional[str] = None
    dob: Optional[str] = None
    photo_url: Optional[str] = None
    emergency_contact: Optional[str] = None
    goal: Optional[str] = None
    joined_at: datetime = Field(default_factory=utc_now)
    trainer_id: Optional[str] = Field(default=None, index=True)
    status_override: Optional[str] = None  # manual override if set
    notes: Optional[str] = None
    leave_reason: Optional[str] = None
    deleted: bool = Field(default=False, index=True)


class HealthForm(BaseUUIDModel, table=True):
    __tablename__ = "health_forms"

    member_id: str = Field(nullable=False, index=True)
    par_q_json: str = Field(default="{}")
    injuries: Optional[str] = None
    conditions: Optional[str] = None
    flagged: bool = Field(default=False)
    signed_name: Optional[str] = None
    signed_at: Optional[datetime] = None
