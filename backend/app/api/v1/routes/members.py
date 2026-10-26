from datetime import date, datetime
import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlmodel import Session, select, func
from app.db.session import get_session
from app.models.ai import ChurnScore
from app.models.base import utc_now
from app.models.checkin import CheckIn
from app.models.member import HealthForm, Member
from app.models.payment import Due, Payment
from app.models.plan import Freeze, Membership, MembershipPlan
from app.models.user import User
from app.schemas.api import FreezeRequest, HealthFormCreate, MemberCreate, MemberUpdate
from app.security.dependencies import get_current_user, require_role
from app.services.membership_service import (
    check_member_limit,
    compute_membership_status,
    freeze_membership,
    get_gym_grace_days,
    renew_or_create_membership,
)
from app.services.payment_service import record_payment

router = APIRouter(prefix="/members", tags=["members"])


@router.get("/")
def list_members(
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    risk_filter: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    gym_id = current_user.gym_id
    query = select(Member).where(Member.gym_id == gym_id, Member.deleted == False)

    if search:
        s = f"%{search.strip()}%"
        query = query.where(
            (Member.name.ilike(s)) | (Member.phone.ilike(s)) | (Member.member_code.ilike(s))
        )

    all_members = session.exec(query.order_by(Member.created_at.desc())).all()
    grace_days = get_gym_grace_days(session, gym_id)

    # Process statuses and risks
    enriched = []
    for m in all_members:
        latest_ms = session.exec(
            select(Membership)
            .where(Membership.gym_id == gym_id, Membership.member_id == m.id)
            .order_by(Membership.end_date.desc())
        ).first()

        computed_status = compute_membership_status(latest_ms, grace_days=grace_days)
        if m.status_override:
            computed_status = m.status_override

        if status_filter and status_filter.lower() != "all" and computed_status != status_filter.lower():
            continue

        churn = session.exec(
            select(ChurnScore).where(ChurnScore.gym_id == gym_id, ChurnScore.member_id == m.id)
        ).first()
        risk_level = churn.level.lower() if churn else "low"

        if risk_filter and risk_filter.lower() != "all" and risk_level != risk_filter.lower():
            continue

        plan_name = "None"
        days_left = 0
        if latest_ms:
            p = session.get(MembershipPlan, latest_ms.plan_id)
            if p:
                plan_name = p.name
            if latest_ms.end_date >= date.today():
                days_left = (latest_ms.end_date - date.today()).days

        # check-ins count
        visits_count = session.exec(
            select(func.count(CheckIn.id)).where(
                CheckIn.gym_id == gym_id, CheckIn.member_id == m.id, CheckIn.result == "ok"
            )
        ).one()

        enriched.append({
            "id": m.id,
            "member_code": m.member_code,
            "name": m.name,
            "phone": m.phone,
            "email": m.email,
            "goal": m.goal,
            "plan": plan_name,
            "status": computed_status,
            "visits": visits_count,
            "days_left": days_left,
            "renewal": latest_ms.end_date.strftime("%b %d, %Y") if latest_ms else "N/A",
            "risk": risk_level,
            "photo_url": m.photo_url,
            "created_at": m.created_at.isoformat(),
        })

    # Pagination
    total = len(enriched)
    start = (page - 1) * limit
    paged = enriched[start : start + limit]

    return {
        "items": paged,
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_member(
    req: MemberCreate,
    current_user: User = Depends(require_role(["owner", "manager", "front_desk"])),
    session: Session = Depends(get_session),
):
    gym_id = current_user.gym_id
    # Enforce plan limits
    check_member_limit(session, gym_id)

    # Generate sequential member code
    count = session.exec(
        select(func.count(Member.id)).where(Member.gym_id == gym_id)
    ).one()
    member_code = f"IPF-{1000 + count + 1}"

    member = Member(
        gym_id=gym_id,
        member_code=member_code,
        name=req.name,
        phone=req.phone,
        email=req.email,
        gender=req.gender,
        dob=req.dob,
        photo_url=req.photo_url,
        emergency_contact=req.emergency_contact,
        goal=req.goal,
        notes=req.notes,
    )
    session.add(member)
    session.commit()
    session.refresh(member)

    # If plan selected, create membership
    if req.plan_id:
        membership = renew_or_create_membership(session, member.id, req.plan_id, gym_id)
        if req.amount_paid_cents and req.amount_paid_cents > 0:
            record_payment(
                session=session,
                gym_id=gym_id,
                member_id=member.id,
                membership_id=membership.id,
                amount_cents=req.amount_paid_cents,
                method=req.payment_method or "cash",
                received_by=current_user.name,
                note="Initial joining payment",
            )

    return {
        "id": member.id,
        "member_code": member.member_code,
        "name": member.name,
        "phone": member.phone,
        "email": member.email,
        "status": "active",
    }


@router.get("/{id}")
def get_member(
    id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    gym_id = current_user.gym_id
    member = session.get(Member, id)
    if not member or member.gym_id != gym_id or member.deleted:
        raise HTTPException(status_code=404, detail="Member not found")

    grace_days = get_gym_grace_days(session, gym_id)
    latest_ms = session.exec(
        select(Membership)
        .where(Membership.gym_id == gym_id, Membership.member_id == member.id)
        .order_by(Membership.end_date.desc())
    ).first()

    computed_status = compute_membership_status(latest_ms, grace_days=grace_days)
    if member.status_override:
        computed_status = member.status_override

    plan_info = None
    if latest_ms:
        p = session.get(MembershipPlan, latest_ms.plan_id)
        plan_info = {
            "membership_id": latest_ms.id,
            "plan_id": p.id if p else None,
            "name": p.name if p else "Standard",
            "start_date": latest_ms.start_date.isoformat(),
            "end_date": latest_ms.end_date.isoformat(),
            "days_left": max(0, (latest_ms.end_date - date.today()).days),
            "status": computed_status,
        }

    # Health form
    hf = session.exec(
        select(HealthForm).where(HealthForm.gym_id == gym_id, HealthForm.member_id == member.id)
    ).first()

    # Payments & Dues
    payments = session.exec(
        select(Payment).where(Payment.gym_id == gym_id, Payment.member_id == member.id).order_by(Payment.paid_at.desc())
    ).all()

    dues = session.exec(
        select(Due).where(Due.gym_id == gym_id, Due.member_id == member.id, Due.status == "open")
    ).all()

    # Visits history
    visits = session.exec(
        select(CheckIn).where(CheckIn.gym_id == gym_id, CheckIn.member_id == member.id).order_by(CheckIn.checked_in_at.desc()).limit(20)
    ).all()

    # Churn
    churn = session.exec(
        select(ChurnScore).where(ChurnScore.gym_id == gym_id, ChurnScore.member_id == member.id)
    ).first()

    return {
        "member": {
            "id": member.id,
            "member_code": member.member_code,
            "name": member.name,
            "phone": member.phone,
            "email": member.email,
            "gender": member.gender,
            "dob": member.dob,
            "photo_url": member.photo_url,
            "emergency_contact": member.emergency_contact,
            "goal": member.goal,
            "notes": member.notes,
            "status": computed_status,
            "joined_at": member.joined_at.isoformat(),
        },
        "plan": plan_info,
        "health_form": {
            "flagged": hf.flagged if hf else False,
            "injuries": hf.injuries if hf else None,
            "signed_name": hf.signed_name if hf else None,
        } if hf else None,
        "payments": [
            {
                "id": p.id,
                "invoice_no": p.invoice_no,
                "amount_cents": p.amount_cents,
                "method": p.method,
                "paid_at": p.paid_at.isoformat(),
                "note": p.note,
            }
            for p in payments
        ],
        "dues": [
            {"id": d.id, "amount_cents": d.amount_cents, "due_date": d.due_date.isoformat(), "reason": d.reason}
            for d in dues
        ],
        "visits": [
            {"id": v.id, "checked_in_at": v.checked_in_at.isoformat(), "method": v.method, "result": v.result}
            for v in visits
        ],
        "churn": {
            "score": churn.score if churn else 10,
            "level": churn.level if churn else "Low",
            "reasons": json.loads(churn.reasons_json) if churn else [],
        },
    }


@router.put("/{id}")
def update_member(
    id: str,
    req: MemberUpdate,
    current_user: User = Depends(require_role(["owner", "manager", "front_desk"])),
    session: Session = Depends(get_session),
):
    member = session.get(Member, id)
    if not member or member.gym_id != current_user.gym_id or member.deleted:
        raise HTTPException(status_code=404, detail="Member not found")

    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(member, k, v)
    member.updated_at = utc_now()
    session.add(member)
    session.commit()
    session.refresh(member)
    return {"status": "updated", "id": member.id}


@router.delete("/{id}")
def delete_member(
    id: str,
    current_user: User = Depends(require_role(["owner", "manager"])),
    session: Session = Depends(get_session),
):
    member = session.get(Member, id)
    if not member or member.gym_id != current_user.gym_id:
        raise HTTPException(status_code=404, detail="Member not found")
    # Soft delete: never hard delete
    member.deleted = True
    member.updated_at = utc_now()
    session.add(member)
    session.commit()
    return {"status": "deleted", "id": member.id}


@router.post("/{id}/freeze")
def freeze_member(
    id: str,
    req: FreezeRequest,
    current_user: User = Depends(require_role(["owner", "manager", "front_desk"])),
    session: Session = Depends(get_session),
):
    latest_ms = session.exec(
        select(Membership)
        .where(Membership.gym_id == current_user.gym_id, Membership.member_id == id)
        .order_by(Membership.end_date.desc())
    ).first()
    if not latest_ms:
        raise HTTPException(status_code=404, detail="No active membership found to freeze")

    updated = freeze_membership(
        session=session,
        membership_id=latest_ms.id,
        freeze_days=req.freeze_days,
        reason=req.reason,
        gym_id=current_user.gym_id,
    )
    return {
        "status": "frozen",
        "new_end_date": updated.end_date.isoformat(),
        "frozen_days_used": updated.frozen_days_used,
    }


@router.post("/{id}/leave")
def member_leave(
    id: str,
    reason: str = Query(...),
    current_user: User = Depends(require_role(["owner", "manager", "front_desk"])),
    session: Session = Depends(get_session),
):
    member = session.get(Member, id)
    if not member or member.gym_id != current_user.gym_id:
        raise HTTPException(status_code=404, detail="Member not found")
    member.status_override = "stopped"
    member.leave_reason = reason
    member.updated_at = utc_now()
    session.add(member)
    session.commit()
    return {"status": "stopped", "reason": reason}


@router.post("/{id}/health-form")
def save_health_form(
    id: str,
    req: HealthFormCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    gym_id = current_user.gym_id
    member = session.get(Member, id)
    if not member or member.gym_id != gym_id:
        raise HTTPException(status_code=404, detail="Member not found")

    hf = session.exec(
        select(HealthForm).where(HealthForm.gym_id == gym_id, HealthForm.member_id == id)
    ).first()

    if not hf:
        hf = HealthForm(gym_id=gym_id, member_id=id)

    hf.par_q_json = req.par_q_json or "{}"
    hf.injuries = req.injuries
    hf.conditions = req.conditions
    hf.flagged = req.flagged
    hf.signed_name = req.signed_name
    hf.signed_at = utc_now()
    hf.updated_at = utc_now()

    session.add(hf)
    session.commit()
    return {"status": "saved", "flagged": hf.flagged}


@router.get("/export/csv")
def export_members_csv(
    current_user: User = Depends(require_role(["owner", "manager"])),
    session: Session = Depends(get_session),
):
    gym_id = current_user.gym_id
    members = session.exec(select(Member).where(Member.gym_id == gym_id, Member.deleted == False)).all()

    lines = ["Member Code,Name,Phone,Email,Goal,Joined Date"]
    for m in members:
        lines.append(f'"{m.member_code}","{m.name}","{m.phone}","{m.email or ""}","{m.goal or ""}","{m.joined_at.strftime("%Y-%m-%d")}"')

    csv_data = "\n".join(lines)
    return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=members.csv"})
