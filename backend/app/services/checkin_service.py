from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.models.base import utc_now
from app.models.checkin import CheckIn
from app.models.gym import GymSettings
from app.models.member import Member
from app.models.payment import Due
from app.models.plan import Membership, MembershipPlan
from app.security.jwt import decode_token
from app.services.membership_service import (
    compute_membership_status,
    get_gym_grace_days,
)


def process_checkin(
    session: Session,
    gym_id: str,
    identifier: str,
    method: str = "qr",
    source: str = "front_desk",
) -> Dict[str, Any]:
    member: Optional[Member] = None

    # 1. Try decoding as QR token
    if len(identifier) > 50:
        try:
            payload = decode_token(identifier)
            if payload.get("type") == "qr_checkin":
                if payload.get("gym_id") != gym_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"code": "WRONG_GYM", "message": "QR token is for a different gym"},
                    )
                member_id = payload.get("sub")
                member = session.get(Member, member_id)
        except HTTPException:
            raise
        except Exception:
            pass

    # 2. Try looking up by member_code or phone
    if not member:
        clean_id = identifier.strip()
        member = session.exec(
            select(Member).where(
                Member.gym_id == gym_id,
                Member.deleted == False,
                (Member.member_code == clean_id) | (Member.phone == clean_id),
            )
        ).first()

    # 3. Try lookup by member id directly
    if not member:
        member = session.get(Member, identifier)
        if member and (member.gym_id != gym_id or member.deleted):
            member = None

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "MEMBER_NOT_FOUND", "message": "Member not found with provided code, phone, or token"},
        )

    # Calculate status
    grace_days = get_gym_grace_days(session, gym_id)
    latest_membership = session.exec(
        select(Membership)
        .where(Membership.gym_id == gym_id, Membership.member_id == member.id)
        .order_by(Membership.end_date.desc())
    ).first()

    computed_status = compute_membership_status(latest_membership, grace_days=grace_days)
    if member.status_override:
        computed_status = member.status_override

    # Check dues
    open_dues = session.exec(
        select(Due).where(
            Due.gym_id == gym_id,
            Due.member_id == member.id,
            Due.status == "open",
        )
    ).all()
    dues_total_cents = sum(d.amount_cents for d in open_dues)

    plan_name = "No Plan"
    days_left = 0
    if latest_membership:
        plan = session.get(MembershipPlan, latest_membership.plan_id)
        if plan:
            plan_name = plan.name
        if latest_membership.end_date >= date.today():
            days_left = (latest_membership.end_date - date.today()).days

    # Determine ok or blocked
    result = "ok"
    blocked_reason = None

    if computed_status == "expired":
        result = "blocked"
        blocked_reason = "Membership expired. Please renew."
    elif computed_status == "frozen":
        result = "blocked"
        blocked_reason = "Membership is currently frozen."
    elif computed_status == "blocked":
        result = "blocked"
        blocked_reason = "Access blocked by gym management."
    elif computed_status == "grace":
        result = "ok"
        blocked_reason = "Membership in grace period. Please renew."

    # Save check-in record
    check_in = CheckIn(
        gym_id=gym_id,
        member_id=member.id,
        checked_in_at=utc_now(),
        method=method,
        result=result,
        blocked_reason=blocked_reason,
        source=source,
    )
    session.add(check_in)
    session.commit()
    session.refresh(check_in)

    return {
        "checkin_id": check_in.id,
        "result": result,
        "blocked_reason": blocked_reason,
        "checked_in_at": check_in.checked_in_at.isoformat(),
        "member": {
            "id": member.id,
            "member_code": member.member_code,
            "name": member.name,
            "phone": member.phone,
            "photo_url": member.photo_url,
            "status": computed_status,
            "plan_name": plan_name,
            "days_left": days_left,
            "dues_cents": dues_total_cents,
        },
    }


def process_checkout(session: Session, checkin_id: str, gym_id: str) -> CheckIn:
    check_in = session.get(CheckIn, checkin_id)
    if not check_in or check_in.gym_id != gym_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CHECKIN_NOT_FOUND", "message": "Check-in record not found"},
        )
    check_in.checked_out_at = utc_now()
    check_in.updated_at = utc_now()
    session.add(check_in)
    session.commit()
    session.refresh(check_in)
    return check_in


def get_live_attendance(session: Session, gym_id: str, auto_checkout_hours: Optional[int] = None) -> Dict[str, Any]:
    if auto_checkout_hours is None:
        gym_settings = session.exec(
            select(GymSettings).where(GymSettings.gym_id == gym_id)
        ).first()
        auto_checkout_hours = gym_settings.auto_checkout_hours if gym_settings else 3

    cutoff = utc_now() - timedelta(hours=auto_checkout_hours)

    active_checkins = session.exec(
        select(CheckIn).where(
            CheckIn.gym_id == gym_id,
            CheckIn.result == "ok",
            CheckIn.checked_in_at >= cutoff,
            CheckIn.checked_out_at == None,
        )
    ).all()

    # get member summaries
    member_ids = [c.member_id for c in active_checkins]
    members = []
    if member_ids:
        members_data = session.exec(
            select(Member).where(Member.id.in_(member_ids))
        ).all()
        m_map = {m.id: m for m in members_data}
        for c in active_checkins:
            m = m_map.get(c.member_id)
            if m:
                members.append({
                    "checkin_id": c.id,
                    "member_id": m.id,
                    "member_code": m.member_code,
                    "name": m.name,
                    "photo_url": m.photo_url,
                    "checked_in_at": c.checked_in_at.isoformat(),
                })

    return {
        "live_count": len(active_checkins),
        "cutoff_hours": auto_checkout_hours,
        "attendees": members,
    }
