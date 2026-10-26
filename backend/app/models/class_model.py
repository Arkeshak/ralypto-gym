from datetime import datetime
from typing import Optional
from sqlmodel import Field
from app.models.base import BaseUUIDModel


class Class(BaseUUIDModel, table=True):
    __tablename__ = "classes"

    name: str = Field(nullable=False, index=True)
    description: Optional[str] = None
    trainer_id: Optional[str] = Field(default=None, index=True)
    room: str = Field(default="Studio A")
    capacity: int = Field(default=20)
    duration_min: int = Field(default=60)
    active: bool = Field(default=True)


class ClassSession(BaseUUIDModel, table=True):
    __tablename__ = "class_sessions"

    class_id: str = Field(nullable=False, index=True)
    starts_at: datetime = Field(nullable=False, index=True)
    capacity: int = Field(default=20)
    status: str = Field(default="scheduled", index=True)  # scheduled, completed, cancelled


class Booking(BaseUUIDModel, table=True):
    __tablename__ = "bookings"

    session_id: str = Field(nullable=False, index=True)
    member_id: str = Field(nullable=False, index=True)
    status: str = Field(default="booked", index=True)  # booked, cancelled, attended, no_show, waitlist
