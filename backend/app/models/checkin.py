from datetime import datetime
from typing import Optional
from sqlmodel import Field
from app.models.base import BaseUUIDModel, utc_now


class CheckIn(BaseUUIDModel, table=True):
    __tablename__ = "check_ins"

    member_id: str = Field(nullable=False, index=True)
    checked_in_at: datetime = Field(default_factory=utc_now, index=True)
    checked_out_at: Optional[datetime] = None
    method: str = Field(default="qr")  # qr, phone, manual
    result: str = Field(default="ok")  # ok, blocked
    blocked_reason: Optional[str] = None
    source: str = Field(default="front_desk")
