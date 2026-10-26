from datetime import date, datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlmodel import Session, select, func
from app.db.session import get_session
from app.models.ai import ChurnScore
from app.models.checkin import CheckIn
from app.models.member import Member
from app.models.payment import Due, Payment
from app.models.plan import Membership, MembershipPlan
from app.models.user import User
from app.security.dependencies import get_current_user
from app.services.checkin_service import get_live_attendance
from app.services.membership_service import (
    compute_membership_status,
    format_money,
    get_gym_grace_days,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard-stats")
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    gym_id = current_user.gym_id
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)

    # 1. Total members & statuses
    all_members = session.exec(select(Member).where(Member.gym_id == gym_id, Member.deleted == False)).all()
    grace_days = get_gym_grace_days(session, gym_id)

    active_count = 0
    expiring_count = 0
    for m in all_members:
        latest_ms = session.exec(
            select(Membership)
            .where(Membership.gym_id == gym_id, Membership.member_id == m.id)
            .order_by(Membership.end_date.desc())
        ).first()
        st = compute_membership_status(latest_ms, grace_days=grace_days)
        if st in ["active", "expiring"]:
            active_count += 1
        if st == "expiring":
            expiring_count += 1

    # 2. Today's check-ins
    today_checkins = session.exec(
        select(func.count(CheckIn.id)).where(
            CheckIn.gym_id == gym_id,
            CheckIn.checked_in_at >= today_start,
            CheckIn.result == "ok",
        )
    ).one()

    # 3. Today's revenue
    today_pmts = session.exec(
        select(Payment).where(
            Payment.gym_id == gym_id,
            Payment.paid_at >= today_start,
        )
    ).all()
    today_rev_cents = sum(p.amount_cents for p in today_pmts)

    # 4. Open dues total
    open_dues = session.exec(select(Due).where(Due.gym_id == gym_id, Due.status == "open")).all()
    dues_total_cents = sum(d.amount_cents for d in open_dues)

    # 5. Live people in gym
    live_info = get_live_attendance(session, gym_id)

    # 6. At risk count
    at_risk_count = session.exec(
        select(func.count(ChurnScore.id)).where(ChurnScore.gym_id == gym_id, ChurnScore.score >= 60)
    ).one()

    return {
        "active_members": active_count,
        "expiring_this_week": expiring_count,
        "today_checkins": today_checkins,
        "today_revenue_cents": today_rev_cents,
        "today_revenue_formatted": format_money(today_rev_cents),
        "dues_total_cents": dues_total_cents,
        "dues_total_formatted": format_money(dues_total_cents),
        "people_in_gym": live_info["live_count"],
        "at_risk_members": at_risk_count,
    }


@router.get("/revenue-chart")
def get_revenue_chart(
    days: int = Query(default=7, ge=7, le=90),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    gym_id = current_user.gym_id
    today = date.today()
    start_date = today - timedelta(days=days - 1)

    chart = []
    for i in range(days):
        day_date = start_date + timedelta(days=i)
        day_start = datetime.combine(day_date, datetime.min.time(), tzinfo=timezone.utc)
        day_end = datetime.combine(day_date, datetime.max.time(), tzinfo=timezone.utc)

        pmts = session.exec(
            select(Payment).where(
                Payment.gym_id == gym_id,
                Payment.paid_at >= day_start,
                Payment.paid_at <= day_end,
            )
        ).all()

        checkins = session.exec(
            select(func.count(CheckIn.id)).where(
                CheckIn.gym_id == gym_id,
                CheckIn.checked_in_at >= day_start,
                CheckIn.checked_in_at <= day_end,
                CheckIn.result == "ok",
            )
        ).one()

        rev = sum(p.amount_cents for p in pmts)
        chart.append({
            "date": day_date.strftime("%Y-%m-%d"),
            "day": day_date.strftime("%a"),
            "revenue": rev / 100.0,
            "visits": checkins,
        })
    return chart
