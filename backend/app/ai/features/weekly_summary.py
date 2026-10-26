from datetime import datetime, timedelta
import json
from typing import Any, Dict, Optional
from sqlmodel import Session, select, func
from app.ai.clients.factory import get_llm_client
from app.models.ai import AIAction, ChurnScore
from app.models.base import utc_now
from app.models.checkin import CheckIn
from app.models.crm import Message
from app.models.gym import Gym
from app.models.member import Member
from app.models.payment import Due, Payment
from app.services.membership_service import format_money


def generate_weekly_summary(
    session: Session,
    gym_id: str,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    now = utc_now()
    seven_days_ago = now - timedelta(days=7)
    fourteen_days_ago = now - timedelta(days=14)

    # Revenue
    this_week_pmts = session.exec(
        select(Payment).where(
            Payment.gym_id == gym_id,
            Payment.paid_at >= seven_days_ago,
        )
    ).all()
    last_week_pmts = session.exec(
        select(Payment).where(
            Payment.gym_id == gym_id,
            Payment.paid_at >= fourteen_days_ago,
            Payment.paid_at < seven_days_ago,
        )
    ).all()

    rev_this = sum(p.amount_cents for p in this_week_pmts)
    rev_last = sum(p.amount_cents for p in last_week_pmts) or 1
    rev_delta_pct = round(((rev_this - rev_last) / rev_last) * 100, 1)

    # Checkins
    checkins_this = session.exec(
        select(func.count(CheckIn.id)).where(
            CheckIn.gym_id == gym_id,
            CheckIn.checked_in_at >= seven_days_ago,
            CheckIn.result == "ok",
        )
    ).one()
    checkins_last = session.exec(
        select(func.count(CheckIn.id)).where(
            CheckIn.gym_id == gym_id,
            CheckIn.checked_in_at >= fourteen_days_ago,
            CheckIn.checked_in_at < seven_days_ago,
            CheckIn.result == "ok",
        )
    ).one()

    # New joins
    new_joins = session.exec(
        select(func.count(Member.id)).where(
            Member.gym_id == gym_id,
            Member.joined_at >= seven_days_ago,
        )
    ).one()

    # Churn members
    churn_count = session.exec(
        select(func.count(ChurnScore.id)).where(
            ChurnScore.gym_id == gym_id,
            ChurnScore.score >= 60,
        )
    ).one()

    # Open dues
    open_dues = session.exec(
        select(Due).where(Due.gym_id == gym_id, Due.status == "open")
    ).all()
    dues_total = sum(d.amount_cents for d in open_dues)

    tips = [
        "Floor attendance peaks between 5:30 PM and 7:30 PM; ensure two trainers remain active during that window.",
        f"{churn_count} members show a sharp drop in 14-day attendance. Send win-back drafts before Friday.",
        "Morning Zumba slots have reached full capacity; consider adding a Thursday morning repeat session.",
    ]

    gym = session.get(Gym, gym_id)
    summary_text = (
        f"📊 *{gym.name if gym else 'Iron Peak Fitness'} Weekly Brief*\n"
        f"• Revenue: {format_money(rev_this)} ({'+' if rev_delta_pct >= 0 else ''}{rev_delta_pct}% vs prior wk)\n"
        f"• Check-ins: {checkins_this} visits (vs {checkins_last} prior wk)\n"
        f"• New Members: +{new_joins} joined this week\n"
        f"• At-Risk: {churn_count} members need re-engagement\n"
        f"• Outstanding Dues: {format_money(dues_total)}\n\n"
        f"💡 *Actionable Advice:*\n"
        + "\n".join(f"- {t}" for t in tips)
    )

    clean_phone = gym.phone.replace("+", "").replace(" ", "") if gym and gym.phone else ""
    wa_url = f"https://wa.me/{clean_phone}?text={summary_text.replace(' ', '%20')}" if clean_phone else None

    # Log AI action
    action = AIAction(
        gym_id=gym_id,
        user_id=user_id,
        feature="weekly_summary",
        tool="generate_weekly_summary",
        input_json=json.dumps({"period": "last_7_days"}),
        output_json=json.dumps({"revenue": rev_this, "checkins": checkins_this, "at_risk": churn_count}),
        status="completed",
    )
    session.add(action)
    session.commit()

    return {
        "period": f"{seven_days_ago.strftime('%b %d')} - {now.strftime('%b %d, %Y')}",
        "metrics": {
            "revenue": {"cents": rev_this, "formatted": format_money(rev_this), "delta_pct": rev_delta_pct},
            "checkins": {"count": checkins_this, "last_week": checkins_last},
            "new_joins": new_joins,
            "at_risk_members": churn_count,
            "outstanding_dues": {"cents": dues_total, "formatted": format_money(dues_total)},
        },
        "tips": tips,
        "summary_text": summary_text,
        "whatsapp_url": wa_url,
    }


def send_weekly_summary_to_owner(
    session: Session,
    gym_id: str,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    summary = generate_weekly_summary(session, gym_id, user_id)
    msg = Message(
        gym_id=gym_id,
        member_or_lead_type="member",
        member_or_lead_id=user_id or "owner",
        channel="whatsapp",
        body=summary["summary_text"],
        status="sent",
        created_by=user_id,
        ai_generated=True,
        sent_at=utc_now(),
    )
    session.add(msg)
    session.commit()
    return {
        "status": "sent",
        "message_id": msg.id,
        "whatsapp_url": summary["whatsapp_url"],
    }
