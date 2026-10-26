from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.plan import MembershipPlan
from app.models.user import User
from app.schemas.api import PlanCreate
from app.security.dependencies import get_current_user, require_role
from app.services.membership_service import format_money, renew_or_create_membership

router = APIRouter(prefix="/membership-plans", tags=["membership-plans"])


@router.get("/")
def list_plans(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    gym_id = current_user.gym_id
    plans = session.exec(
        select(MembershipPlan).where(MembershipPlan.gym_id == gym_id)
    ).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "duration_days": p.duration_days,
            "price_cents": p.price_cents,
            "price_formatted": format_money(p.price_cents),
            "joining_fee_cents": p.joining_fee_cents,
            "max_freeze_days": p.max_freeze_days,
            "active": p.active,
        }
        for p in plans
    ]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_plan(
    req: PlanCreate,
    current_user: User = Depends(require_role(["owner", "manager"])),
    session: Session = Depends(get_session),
):
    plan = MembershipPlan(
        gym_id=current_user.gym_id,
        name=req.name,
        duration_days=req.duration_days,
        price_cents=req.price_cents,
        joining_fee_cents=req.joining_fee_cents,
        max_freeze_days=req.max_freeze_days,
        active=req.active,
    )
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


@router.post("/members/{member_id}/assign")
def assign_membership(
    member_id: str,
    plan_id: str,
    current_user: User = Depends(require_role(["owner", "manager", "front_desk"])),
    session: Session = Depends(get_session),
):
    membership = renew_or_create_membership(
        session=session,
        member_id=member_id,
        plan_id=plan_id,
        gym_id=current_user.gym_id,
    )
    return {
        "membership_id": membership.id,
        "start_date": membership.start_date.isoformat(),
        "end_date": membership.end_date.isoformat(),
        "status": membership.status,
    }
