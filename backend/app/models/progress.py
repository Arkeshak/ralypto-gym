from datetime import date as dt_date
from typing import Optional
from sqlmodel import Field
from app.models.base import BaseUUIDModel


class Measurement(BaseUUIDModel, table=True):
    __tablename__ = "measurements"

    member_id: str = Field(nullable=False, index=True)
    date: dt_date = Field(default_factory=dt_date.today)
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    hips_cm: Optional[float] = None
    notes: Optional[str] = None


class Goal(BaseUUIDModel, table=True):
    __tablename__ = "goals"

    member_id: str = Field(nullable=False, index=True)
    type: str = Field(nullable=False)  # weight_loss, muscle_gain, strength, endurance
    target: str = Field(nullable=False)  # e.g. "Lose 5kg", "Bench 100kg"
    due_date: Optional[dt_date] = None
    status: str = Field(default="in_progress", index=True)  # in_progress, achieved, abandoned
