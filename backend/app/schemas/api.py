from datetime import date as dt_date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# Auth Schemas
class LoginRequest(BaseModel):
    email: str
    password: str


class PinLoginRequest(BaseModel):
    gym_code: str = "IPF"
    pin: str


class MemberLoginRequest(BaseModel):
    phone: str
    code: str = "123456"


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    role: str
    gym_id: str


class AuthMeResponse(BaseModel):
    user_id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    role: str
    language: str
    gym_id: str
    gym_name: str
    plan: str
    plan_status: str
    features: List[str]
    member_limit: int
    current_member_count: int
    linked_member_id: Optional[str] = None


# Member Schemas
class MemberCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[str] = None
    photo_url: Optional[str] = None
    emergency_contact: Optional[str] = None
    goal: Optional[str] = None
    notes: Optional[str] = None
    plan_id: Optional[str] = None
    amount_paid_cents: Optional[int] = None
    payment_method: Optional[str] = "cash"


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[str] = None
    photo_url: Optional[str] = None
    emergency_contact: Optional[str] = None
    goal: Optional[str] = None
    notes: Optional[str] = None
    status_override: Optional[str] = None


class HealthFormCreate(BaseModel):
    par_q_json: Optional[str] = "{}"
    injuries: Optional[str] = None
    conditions: Optional[str] = None
    flagged: bool = False
    signed_name: Optional[str] = None


# Plan Schemas
class PlanCreate(BaseModel):
    name: str
    duration_days: int = 30
    price_cents: int
    joining_fee_cents: int = 0
    max_freeze_days: int = 30
    active: bool = True


# Payment Schemas
class PaymentCreate(BaseModel):
    member_id: str
    amount_cents: int
    method: str = "cash"
    membership_id: Optional[str] = None
    reference: Optional[str] = None
    note: Optional[str] = None


# Check-in Schemas
class CheckInRequest(BaseModel):
    identifier: str  # member_code, phone, or signed QR token
    method: str = "qr"  # qr, phone, manual


# Class Schemas
class ClassCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trainer_id: Optional[str] = None
    room: str = "Studio A"
    capacity: int = 20
    duration_min: int = 60


class ClassSessionCreate(BaseModel):
    class_id: str
    starts_at: datetime
    capacity: int = 20


# Workout Schemas
class ExerciseCreate(BaseModel):
    name: str
    muscle_group: str
    equipment: str = "bodyweight"
    level: str = "beginner"
    how_to: Optional[str] = None
    media_url: Optional[str] = None
    contraindications_json: str = "[]"


class WorkoutLogCreate(BaseModel):
    member_id: str
    exercise_id: str
    plan_id: Optional[str] = None
    date: dt_date = Field(default_factory=dt_date.today)
    sets_json: str = "[]"


# AI Schemas
class WinbackDraftRequest(BaseModel):
    member_id: str
    offer: Optional[str] = "15% off renewal"


class CoachPlanRequest(BaseModel):
    member_id: str
    goal: str = "Build strength"
    level: str = "beginner"
    days_per_week: int = 3


class AssistantChatRequest(BaseModel):
    query: str
    confirm_action: Optional[Dict[str, Any]] = None


class AskGymRequest(BaseModel):
    query: str


class FreezeRequest(BaseModel):
    freeze_days: int = 14
    reason: Optional[str] = "Vacation/Injury"


class PlanSwitchRequest(BaseModel):
    plan: str  # Basic, Standard, Premium
