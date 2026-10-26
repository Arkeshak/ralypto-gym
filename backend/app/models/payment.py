from datetime import date, datetime
from typing import Optional
from sqlmodel import Field
from app.models.base import BaseUUIDModel, utc_now


class Payment(BaseUUIDModel, table=True):
    __tablename__ = "payments"

    member_id: str = Field(nullable=False, index=True)
    membership_id: Optional[str] = Field(default=None, index=True)
    amount_cents: int = Field(nullable=False)
    method: str = Field(default="cash")  # cash, card, bank, online
    reference: Optional[str] = None
    invoice_no: str = Field(nullable=False, index=True)
    received_by: Optional[str] = None
    paid_at: datetime = Field(default_factory=utc_now)
    note: Optional[str] = None


class Due(BaseUUIDModel, table=True):
    __tablename__ = "dues"

    member_id: str = Field(nullable=False, index=True)
    amount_cents: int = Field(nullable=False)
    due_date: date = Field(nullable=False)
    status: str = Field(default="open", index=True)  # open, paid
    reason: Optional[str] = None
