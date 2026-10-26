from datetime import date, datetime, timedelta
import json
from typing import Any, Dict, List, Optional
from sqlmodel import Session, select
from app.ai.clients.factory import get_llm_client
from app.models.ai import AIAction, ChurnScore
from app.models.base import utc_now
from app.models.checkin import CheckIn
from app.models.crm import Message
from app.models.member import Member
from app.models.payment import Due
from app.models.plan import Membership


def compute_member_churn(session: Session, member: Member, gym_id: str) -> ChurnScore:
    now = utc_now()
    two_weeks_ago = now - timedelta(days=14)
    six_weeks_ago = now - timedelta(days=42)

    # 1. Recent visits (last 14 days)
    recent_visits = session.exec(
        select(CheckIn).where(
            CheckIn.gym_id == gym_id,
            CheckIn.member_id == member.id,
            CheckIn.checked_in_at >= two_weeks_ago,
            CheckIn.result == "ok",
        )
    ).all()
    recent_count = len(recent_visits)

    # Historical visits (previous 28 days to establish baseline)
    baseline_visits = session.exec(
        select(CheckIn).where(
            CheckIn.gym_id == gym_id,
            CheckIn.member_id == member.id,
            CheckIn.checked_in_at >= six_weeks_ago,
            CheckIn.checked_in_at < two_weeks_ago,
            CheckIn.result == "ok",
        )
    ).all()
    # expected 14-day rate from 28-day baseline
    expected_rate = max(1, round(len(baseline_visits) / 2))

    # Last visit timestamp
    last_checkin = session.exec(
        select(CheckIn)
        .where(
            CheckIn.gym_id == gym_id,
            CheckIn.member_id == member.id,
            CheckIn.result == "ok",
        )
        .order_by(CheckIn.checked_in_at.desc())
    ).first()

    days_since_last = (now - last_checkin.checked_in_at).days if last_checkin else 30

    # Membership expiring soon
    latest_membership = session.exec(
        select(Membership)
        .where(Membership.gym_id == gym_id, Membership.member_id == member.id)
        .order_by(Membership.end_date.desc())
    ).first()

    days_to_end = (latest_membership.end_date - date.today()).days if latest_membership else -1

    # Open dues
    dues = session.exec(
        select(Due).where(
            Due.gym_id == gym_id,
            Due.member_id == member.id,
            Due.status == "open",
        )
    ).all()

    # Rule-based scoring calculation
    score = 0
    reasons: List[str] = []

    # Frequency drop
    if recent_count < expected_rate:
        drop_pts = min(40, (expected_rate - recent_count) * 12)
        score += drop_pts
        reasons.append(f"Visited {recent_count} times in last 14 days (usually {expected_rate})")

    # Inactivity gap
    if days_since_last >= 10:
        score += 25
        reasons.append(f"No visit in {days_since_last} days")
    elif days_since_last >= 7:
        score += 15
        reasons.append(f"Last visited {days_since_last} days ago")

    # Ending soon without renewal
    if 0 <= days_to_end <= 14:
        score += 20
        reasons.append(f"Membership ends in {days_to_end} days without renewal")
    elif days_to_end < 0:
        score += 25
        reasons.append("Membership has expired")

    # Dues
    if dues:
        score += 15
        reasons.append(f"Has {len(dues)} open unpaid fee item(s)")

    # New member low attendance
    joined_days = (now - member.joined_at).days
    if joined_days <= 21 and recent_count < 4:
        score += 20
        reasons.append(f"New member with only {recent_count} visits in first 3 weeks")

    score = min(100, max(0, score))
    level = "High" if score >= 60 else ("Medium" if score >= 30 else "Low")

    # Update or create ChurnScore
    existing = session.exec(
        select(ChurnScore).where(
            ChurnScore.gym_id == gym_id,
            ChurnScore.member_id == member.id,
        )
    ).first()

    if existing:
        existing.score = score
        existing.level = level
        existing.reasons_json = json.dumps(reasons)
        existing.computed_at = utc_now()
        session.add(existing)
        record = existing
    else:
        record = ChurnScore(
            gym_id=gym_id,
            member_id=member.id,
            score=score,
            level=level,
            reasons_json=json.dumps(reasons),
            computed_at=utc_now(),
        )
        session.add(record)

    session.commit()
    session.refresh(record)
    return record


def compute_all_churn_scores(session: Session, gym_id: str) -> List[ChurnScore]:
    members = session.exec(
        select(Member).where(Member.gym_id == gym_id, Member.deleted == False)
    ).all()
    results = []
    for m in members:
        results.append(compute_member_churn(session, m, gym_id))
    return results


def draft_winback_message(
    session: Session,
    gym_id: str,
    member_id: str,
    offer: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    member = session.get(Member, member_id)
    if not member or member.gym_id != gym_id:
        raise ValueError("Member not found")

    churn_score = session.exec(
        select(ChurnScore).where(
            ChurnScore.gym_id == gym_id,
            ChurnScore.member_id == member_id,
        )
    ).first()

    reasons = json.loads(churn_score.reasons_json) if churn_score else ["Attendance has decreased recently"]
    reasons_text = ", ".join(reasons)
    pref_lang = getattr(member, "language", "en") or "en"

    prompt = (
        f"Draft a warm, polite win-back message for gym member {member.name}. "
        f"Reasons for risk: {reasons_text}. "
        f"Special offer to include: {offer or '15% off renewal'}. "
        f"Preferred language: {pref_lang}."
    )

    llm = get_llm_client()
    body = llm.generate(prompt=prompt, system="You are an empathetic gym manager writing a short WhatsApp message.")

    # Save as draft message
    msg = Message(
        gym_id=gym_id,
        member_or_lead_type="member",
        member_or_lead_id=member.id,
        channel="whatsapp",
        body=body.strip(),
        status="draft",
        created_by=user_id,
        ai_generated=True,
    )
    session.add(msg)

    # Log AI action
    action = AIAction(
        gym_id=gym_id,
        user_id=user_id,
        feature="winback_agent",
        tool="draft_winback",
        input_json=json.dumps({"member_id": member_id, "offer": offer, "reasons": reasons}),
        output_json=json.dumps({"message_id": msg.id, "body": body}),
        status="completed",
    )
    session.add(action)
    session.commit()
    session.refresh(msg)

    clean_phone = member.phone.replace("+", "").replace(" ", "")
    wa_url = f"https://wa.me/{clean_phone}?text={body.strip().replace(' ', '%20')}"

    return {
        "message_id": msg.id,
        "member_name": member.name,
        "member_phone": member.phone,
        "body": body.strip(),
        "status": msg.status,
        "whatsapp_url": wa_url,
    }
