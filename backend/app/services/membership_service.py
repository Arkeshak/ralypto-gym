from datetime import date, datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session, select, func
from app.core.config import settings
from app.models.base import utc_now
from app.models.gym import Gym, GymSettings
from app.models.member import Member
from app.models.plan import Membership, MembershipPlan, Freeze


def format_money(cents: int) -> str:
    rupees = cents / 100.0
    return f"Rs {rupees:,.2f}" if cents % 100 != 0 else f"Rs {int(rupees):,}"


def compute_membership_status(
    membership: Optional[Membership],
    grace_days: int = 7,
    as_of: Optional[date] = None,
) -> str:
    if not membership:
        return "expired"

    if membership.status == "frozen":
        return "frozen"

    today = as_of or date.today()

    if today < membership.start_date:
        return "active"

    if today <= membership.end_date:
        days_left = (membership.end_date - today).days
        if days_left <= 7:
            return "expiring"
        return "active"

    # today > membership.end_date
    overdue_days = (today - membership.end_date).days
    if overdue_days <= grace_days:
        return "grace"

    return "expired"


def check_member_limit(session: Session, gym_id: str) -> None:
    gym = session.get(Gym, gym_id)
    if not gym:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "GYM_NOT_FOUND", "message": "Gym not found"},
        )
    limit = settings.PLAN_MEMBER_LIMITS.get(gym.plan, 150)
    count = session.exec(
        select(func.count(Member.id)).where(
            Member.gym_id == gym_id,
            Member.deleted == False,
        )
    ).one()
    if count >= limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "MEMBER_LIMIT_REACHED",
                "message": f"Gym has reached the maximum allowed members ({limit}) for the {gym.plan} plan. Upgrade to add more members.",
            },
        )


def get_gym_grace_days(session: Session, gym_id: str) -> int:
    gym_settings = session.exec(
        select(GymSettings).where(GymSettings.gym_id == gym_id)
    ).first()
    return gym_settings.grace_days if gym_settings else 7


def renew_or_create_membership(
    session: Session,
    member_id: str,
    plan_id: str,
    gym_id: str,
) -> Membership:
    plan = session.get(MembershipPlan, plan_id)
    if not plan or plan.gym_id != gym_id or not plan.active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PLAN_NOT_FOUND", "message": "Membership plan not found or inactive"},
        )

    # Find current latest membership for member
    statement = (
        select(Membership)
        .where(Membership.gym_id == gym_id, Membership.member_id == member_id)
        .order_by(Membership.end_date.desc())
    )
    latest = session.exec(statement).first()

    today = date.today()
    if latest and latest.end_date >= today:
        # Extend from current end date
        start = latest.end_date + timedelta(days=1)
    else:
        start = today

    end = start + timedelta(days=plan.duration_days)

    membership = Membership(
        gym_id=gym_id,
        member_id=member_id,
        plan_id=plan_id,
        start_date=start,
        end_date=end,
        status="active",
        frozen_days_used=0,
        auto_renew=False,
    )
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership


def freeze_membership(
    session: Session,
    membership_id: str,
    freeze_days: int,
    reason: Optional[str],
    gym_id: str,
) -> Membership:
    membership = session.get(Membership, membership_id)
    if not membership or membership.gym_id != gym_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "MEMBERSHIP_NOT_FOUND", "message": "Membership not found"},
        )

    plan = session.get(MembershipPlan, membership.plan_id)
    max_days = plan.max_freeze_days if plan else 30
    if membership.frozen_days_used + freeze_days > max_days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "MAX_FREEZE_EXCEEDED",
                "message": f"Cannot freeze for {freeze_days} days. Remaining allowed freeze days: {max_days - membership.frozen_days_used}",
            },
        )

    freeze_start = date.today()
    freeze_end = freeze_start + timedelta(days=freeze_days)

    freeze = Freeze(
        gym_id=gym_id,
        membership_id=membership.id,
        start_date=freeze_start,
        end_date=freeze_end,
        reason=reason,
    )
    session.add(freeze)

    # push end date
    membership.end_date = membership.end_date + timedelta(days=freeze_days)
    membership.frozen_days_used += freeze_days
    membership.status = "frozen"
    membership.updated_at = utc_now()

    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership
