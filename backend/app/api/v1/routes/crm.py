from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.base import utc_now
from app.models.crm import Campaign, Lead, Message
from app.models.member import Member
from app.models.user import User
from app.security.dependencies import get_current_user, require_role

router = APIRouter(prefix="/crm", tags=["crm"])


@router.get("/leads")
def list_leads(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    query = select(Lead).where(Lead.gym_id == current_user.gym_id)
    if status_filter:
        query = query.where(Lead.status == status_filter)
    return session.exec(query.order_by(Lead.created_at.desc())).all()


@router.post("/leads", status_code=status.HTTP_201_CREATED)
def create_lead(
    name: str,
    phone: str,
    email: Optional[str] = None,
    source: str = "walk_in",
    notes: Optional[str] = None,
    current_user: User = Depends(require_role(["owner", "manager", "front_desk"])),
    session: Session = Depends(get_session),
):
    lead = Lead(
        gym_id=current_user.gym_id,
        name=name,
        phone=phone,
        email=email,
        source=source,
        notes=notes,
        status="new",
        score=50,
    )
    session.add(lead)
    session.commit()
    session.refresh(lead)
    return lead


@router.post("/leads/{id}/convert")
def convert_lead_to_member(
    id: str,
    current_user: User = Depends(require_role(["owner", "manager", "front_desk"])),
    session: Session = Depends(get_session),
):
    lead = session.get(Lead, id)
    if not lead or lead.gym_id != current_user.gym_id:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead.status = "joined"
    session.add(lead)

    # create member
    count = session.exec(select(Lead).where(Lead.gym_id == current_user.gym_id)).all()
    member = Member(
        gym_id=current_user.gym_id,
        member_code=f"IPF-{1100 + len(count)}",
        name=lead.name,
        phone=lead.phone,
        email=lead.email,
        goal="Fitness",
        notes=f"Converted from lead: {lead.notes or ''}",
    )
    session.add(member)
    session.commit()
    session.refresh(member)
    return {"status": "converted", "member_id": member.id, "member_code": member.member_code}


@router.get("/messages")
def list_messages(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    query = select(Message).where(Message.gym_id == current_user.gym_id)
    if status_filter:
        query = query.where(Message.status == status_filter)
    return session.exec(query.order_by(Message.created_at.desc())).all()


@router.post("/messages/{id}/send")
def send_message(
    id: str,
    current_user: User = Depends(require_role(["owner", "manager", "front_desk"])),
    session: Session = Depends(get_session),
):
    msg = session.get(Message, id)
    if not msg or msg.gym_id != current_user.gym_id:
        raise HTTPException(status_code=404, detail="Message not found")

    msg.status = "sent"
    msg.sent_at = utc_now()
    session.add(msg)
    session.commit()

    # generate wa link if member
    wa_url = None
    if msg.member_or_lead_type == "member":
        member = session.get(Member, msg.member_or_lead_id)
        if member and member.phone:
            clean_phone = member.phone.replace("+", "").replace(" ", "")
            wa_url = f"https://wa.me/{clean_phone}?text={msg.body.replace(' ', '%20')}"

    return {"status": "sent", "message_id": msg.id, "whatsapp_url": wa_url}
