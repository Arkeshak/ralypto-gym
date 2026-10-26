from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from app.db.session import get_session
from app.models.base import utc_now
from app.models.class_model import Booking, Class, ClassSession
from app.models.gym import GymSettings
from app.models.member import Member
from app.models.user import User
from app.schemas.api import ClassCreate, ClassSessionCreate
from app.security.dependencies import get_current_user, require_feature, require_role

router = APIRouter(prefix="/classes", tags=["classes"])


@router.get("/")
def list_classes(
    current_user: User = Depends(get_current_user),
    _gym=Depends(require_feature("classes")),
    session: Session = Depends(get_session),
):
    gym_id = current_user.gym_id
    classes = session.exec(select(Class).where(Class.gym_id == gym_id)).all()
    return classes


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_class(
    req: ClassCreate,
    current_user: User = Depends(require_role(["owner", "manager"])),
    _gym=Depends(require_feature("classes")),
    session: Session = Depends(get_session),
):
    c = Class(
        gym_id=current_user.gym_id,
        name=req.name,
        description=req.description,
        trainer_id=req.trainer_id,
        room=req.room,
        capacity=req.capacity,
        duration_min=req.duration_min,
        active=True,
    )
    session.add(c)
    session.commit()
    session.refresh(c)
    return c


@router.get("/sessions")
def list_sessions(
    current_user: User = Depends(get_current_user),
    _gym=Depends(require_feature("classes")),
    session: Session = Depends(get_session),
):
    gym_id = current_user.gym_id
    query = (
        select(ClassSession, Class)
        .join(Class, Class.id == ClassSession.class_id)
        .where(ClassSession.gym_id == gym_id)
        .order_by(ClassSession.starts_at.asc())
    )
    results = session.exec(query).all()

    items = []
    for sess, cls in results:
        booked_count = session.exec(
            select(func.count(Booking.id)).where(
                Booking.session_id == sess.id,
                Booking.status.in_(["booked", "attended"]),
            )
        ).one()

        trainer = session.get(User, cls.trainer_id) if cls.trainer_id else None

        items.append({
            "id": sess.id,
            "class_id": cls.id,
            "name": cls.name,
            "trainer": trainer.name if trainer else "Coach",
            "time": sess.starts_at.strftime("%I:%M %p"),
            "starts_at": sess.starts_at.isoformat(),
            "capacity": sess.capacity,
            "booked": booked_count,
            "room": cls.room,
            "status": sess.status,
        })
    return items


@router.post("/sessions/{id}/book")
def book_session(
    id: str,
    member_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    _gym=Depends(require_feature("classes")),
    session: Session = Depends(get_session),
):
    target_member_id = member_id or current_user.linked_member_id or current_user.id
    gym_id = current_user.gym_id

    sess = session.get(ClassSession, id)
    if not sess or sess.gym_id != gym_id:
        raise HTTPException(status_code=404, detail="Class session not found")

    booked_count = session.exec(
        select(func.count(Booking.id)).where(
            Booking.session_id == sess.id,
            Booking.status == "booked",
        )
    ).one()

    booking_status = "booked" if booked_count < sess.capacity else "waitlist"

    booking = Booking(
        gym_id=gym_id,
        session_id=sess.id,
        member_id=target_member_id,
        status=booking_status,
    )
    session.add(booking)
    session.commit()
    session.refresh(booking)

    return {
        "booking_id": booking.id,
        "status": booking.status,
        "is_waitlist": booking_status == "waitlist",
    }


@router.post("/sessions/{id}/cancel")
def cancel_booking(
    id: str,
    member_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    _gym=Depends(require_feature("classes")),
    session: Session = Depends(get_session),
):
    target_member_id = member_id or current_user.linked_member_id or current_user.id
    gym_id = current_user.gym_id

    booking = session.exec(
        select(Booking).where(
            Booking.session_id == id,
            Booking.member_id == target_member_id,
            Booking.status.in_(["booked", "waitlist"]),
        )
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Active booking not found")

    booking.status = "cancelled"
    booking.updated_at = utc_now()
    session.add(booking)

    # Check for waitlist promotion
    waitlist_first = session.exec(
        select(Booking)
        .where(Booking.session_id == id, Booking.status == "waitlist")
        .order_by(Booking.created_at.asc())
    ).first()

    promoted_member = None
    if waitlist_first:
        waitlist_first.status = "booked"
        waitlist_first.updated_at = utc_now()
        session.add(waitlist_first)
        promoted_member = waitlist_first.member_id

    session.commit()

    return {
        "status": "cancelled",
        "promoted_waitlist_member_id": promoted_member,
    }
