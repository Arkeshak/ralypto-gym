from datetime import date as dt_date, datetime
from typing import Optional
from sqlmodel import Field
from app.models.base import BaseUUIDModel


class Exercise(BaseUUIDModel, table=True):
    __tablename__ = "exercises"

    name: str = Field(nullable=False, index=True)
    muscle_group: str = Field(nullable=False, index=True)
    equipment: str = Field(default="bodyweight", index=True)
    level: str = Field(default="beginner")  # beginner, intermediate, advanced
    how_to: Optional[str] = None
    media_url: Optional[str] = None
    contraindications_json: str = Field(default="[]")  # e.g. ["knee_pain", "shoulder_injury"]


class WorkoutPlan(BaseUUIDModel, table=True):
    __tablename__ = "workout_plans"

    member_id: str = Field(nullable=False, index=True)
    created_by: Optional[str] = None
    source: str = Field(default="manual")  # manual, ai, template
    status: str = Field(default="pending_approval", index=True)  # draft, pending_approval, approved, archived
    title: str = Field(nullable=False)
    days_json: str = Field(default="[]")
    notes: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


class WorkoutLog(BaseUUIDModel, table=True):
    __tablename__ = "workout_logs"

    member_id: str = Field(nullable=False, index=True)
    plan_id: Optional[str] = Field(default=None, index=True)
    date: dt_date = Field(default_factory=dt_date.today)
    exercise_id: str = Field(nullable=False, index=True)
    sets_json: str = Field(default="[]")  # e.g. [{"set": 1, "reps": 12, "weight_kg": 20}]


class MealPlan(BaseUUIDModel, table=True):
    __tablename__ = "meal_plans"

    member_id: str = Field(nullable=False, index=True)
    created_by: Optional[str] = None
    source: str = Field(default="manual")  # manual, ai, template
    status: str = Field(default="pending_approval", index=True)  # draft, pending_approval, approved, archived
    title: str = Field(nullable=False)
    days_json: str = Field(default="[]")
    notes: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
