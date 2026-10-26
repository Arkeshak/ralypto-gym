from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.db.session import get_session
from app.models.user import User
from app.schemas.api import CheckInRequest
from app.security.dependencies import get_current_user, require_role
from app.security.jwt import create_qr_token
from app.services.checkin_service import (
    get_live_attendance,
    process_checkin,
    process_checkout,
)

router = APIRouter(prefix="/checkin", tags=["checkin"])


@router.post("/")
def checkin_member(
    req: CheckInRequest,
    current_user: User = Depends(require_role(["owner", "manager", "front_desk", "trainer"])),
    session: Session = Depends(get_session),
):
    return process_checkin(
        session=session,
        gym_id=current_user.gym_id,
        identifier=req.identifier,
        method=req.method,
        source=current_user.role,
    )


@router.post("/{id}/checkout")
def checkout_member(
    id: str,
    current_user: User = Depends(require_role(["owner", "manager", "front_desk"])),
    session: Session = Depends(get_session),
):
    record = process_checkout(session=session, checkin_id=id, gym_id=current_user.gym_id)
    return {"status": "checked_out", "id": record.id}


@router.get("/live")
def live_people(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return get_live_attendance(session=session, gym_id=current_user.gym_id)


@router.get("/qr-token")
def get_my_qr_token(
    current_user: User = Depends(get_current_user),
):
    member_id = current_user.linked_member_id or current_user.id
    token = create_qr_token(gym_id=current_user.gym_id, member_id=member_id, expires_seconds=60)
    return {
        "qr_token": token,
        "expires_in_seconds": 60,
        "member_id": member_id,
    }
