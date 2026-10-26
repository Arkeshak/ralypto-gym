from datetime import datetime
from typing import Optional
from sqlmodel import Field
from app.models.base import BaseUUIDModel


class TrainerSession(BaseUUIDModel, table=True):
    __tablename__ = "trainer_sessions"

    trainer_id: str = Field(nullable=False, index=True)
    member_id: str = Field(nullable=False, index=True)
    starts_at: datetime = Field(nullable=False, index=True)
    status: str = Field(default="scheduled", index=True)  # scheduled, completed, cancelled


class SessionPack(BaseUUIDModel, table=True):
    __tablename__ = "session_packs"

    member_id: str = Field(nullable=False, index=True)
    total: int = Field(default=10)
    used: int = Field(default=0)
