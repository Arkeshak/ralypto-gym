from typing import Optional
from sqlmodel import Field
from app.models.base import BaseUUIDModel


class User(BaseUUIDModel, table=True):
    __tablename__ = "users"

    name: str = Field(nullable=False)
    email: Optional[str] = Field(default=None, index=True)
    phone: Optional[str] = Field(default=None, index=True)
    password_hash: Optional[str] = None
    role: str = Field(default="front_desk", index=True)  # owner, manager, front_desk, trainer, member
    pin_hash: Optional[str] = None
    active: bool = Field(default=True)
    language: str = Field(default="en")  # en, si, ta
    linked_member_id: Optional[str] = Field(default=None, index=True)
