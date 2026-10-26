from datetime import date, datetime
from typing import Optional
from sqlmodel import Field
from app.models.base import BaseUUIDModel


class Lead(BaseUUIDModel, table=True):
    __tablename__ = "leads"

    name: str = Field(nullable=False, index=True)
    phone: str = Field(nullable=False, index=True)
    email: Optional[str] = None
    source: str = Field(default="walk_in")  # walk_in, instagram, referral, web
    status: str = Field(default="new", index=True)  # new, trial, joined, lost
    next_follow_up: Optional[date] = None
    notes: Optional[str] = None
    score: int = Field(default=50)  # 0-100 lead score


class Campaign(BaseUUIDModel, table=True):
    __tablename__ = "campaigns"

    name: str = Field(nullable=False)
    audience_filter_json: str = Field(default="{}")
    message: str = Field(nullable=False)
    status: str = Field(default="draft", index=True)  # draft, active, sent


class Message(BaseUUIDModel, table=True):
    __tablename__ = "messages"

    member_or_lead_type: str = Field(default="member")  # member, lead
    member_or_lead_id: str = Field(nullable=False, index=True)
    channel: str = Field(default="whatsapp")  # whatsapp, sms, in_app
    body: str = Field(nullable=False)
    status: str = Field(default="draft", index=True)  # draft, approved, sent, failed
    created_by: Optional[str] = None
    ai_generated: bool = Field(default=False)
    sent_at: Optional[datetime] = None
