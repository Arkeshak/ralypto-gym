from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.user import User
from app.security.dependencies import require_role
from app.security.passwords import hash_password, hash_pin

router = APIRouter(prefix="/staff", tags=["staff"])


class StaffCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = "front_desk"
    password: Optional[str] = "Pass1234!"
    pin: Optional[str] = "1234"


@router.get("/")
def list_staff(
    current_user: User = Depends(require_role(["owner", "manager"])),
    session: Session = Depends(get_session),
):
    users = session.exec(
        select(User).where(User.gym_id == current_user.gym_id, User.role != "member")
    ).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "phone": u.phone,
            "role": u.role,
            "active": u.active,
            "has_pin": bool(u.pin_hash),
        }
        for u in users
    ]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_staff(
    req: StaffCreate,
    current_user: User = Depends(require_role(["owner"])),
    session: Session = Depends(get_session),
):
    u = User(
        gym_id=current_user.gym_id,
        name=req.name,
        email=req.email,
        phone=req.phone,
        role=req.role,
        password_hash=hash_password(req.password) if req.password else None,
        pin_hash=hash_pin(req.pin) if req.pin else None,
        active=True,
    )
    session.add(u)
    session.commit()
    session.refresh(u)
    return {"id": u.id, "name": u.name, "role": u.role}


@router.post("/{id}/reset-pin")
def reset_staff_pin(
    id: str,
    pin: str,
    current_user: User = Depends(require_role(["owner", "manager"])),
    session: Session = Depends(get_session),
):
    u = session.get(User, id)
    if not u or u.gym_id != current_user.gym_id:
        raise HTTPException(status_code=404, detail="Staff user not found")
    u.pin_hash = hash_pin(pin)
    session.add(u)
    session.commit()
    return {"status": "pin_updated", "id": u.id}
