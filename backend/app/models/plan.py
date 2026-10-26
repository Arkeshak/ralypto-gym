from datetime import date, datetime
from typing import Optional
from sqlmodel import Field
from app.models.base import BaseUUIDModel


class MembershipPlan(BaseUUIDModel, table=True):
    __tablename__ = "membership_plans"

    name: str = Field(nullable=False, index=True)
    duration_days: int = Field(default=30)
    price_cents: int = Field(default=0)
    joining_fee_cents: int = Field(default=0)
    max_freeze_days: int = Field(default=30)
    active: bool = Field(default=True)


class Membership(BaseUUIDModel, table=True):
    __tablename__ = "memberships"

    member_id: str = Field(nullable=False, index=True)
    plan_id: str = Field(nullable=False, index=True)
    start_date: date = Field(nullable=False)
    end_date: date = Field(nullable=False)
    status: str = Field(default="active", index=True)  # active, expiring, grace, expired, frozen
    frozen_days_used: int = Field(default=0)
    auto_renew: bool = Field(default=False)


class Freeze(BaseUUIDModel, table=True):
    __tablename__ = "freezes"

    membership_id: str = Field(nullable=False, index=True)
    start_date: date = Field(nullable=False)
    end_date: date = Field(nullable=False)
    reason: Optional[str] = None
