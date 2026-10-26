from datetime import date, datetime, timedelta
import json
from typing import Any, Dict, List, Optional
from sqlmodel import Session, select
from app.ai.clients.factory import get_llm_client
from app.models.ai import AIAction
from app.models.base import utc_now
from app.models.class_model import Booking, Class, ClassSession
from app.models.member import Member
from app.models.payment import Due
from app.models.plan import Membership, MembershipPlan
from app.models.workout import WorkoutPlan
from app.services.membership_service import compute_membership_status, format_money


def handle_assistant_query(
    session: Session,
    gym_id: str,
    member_id: str,
    query: str,
    confirm_action: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    member = session.get(Member, member_id)
    if not member or member.gym_id != gym_id:
        raise ValueError("Member not found")

    q_lower = query.lower()

    # 1. If this is an execution of a previously confirmed action:
    if confirm_action and confirm_action.get("confirmed"):
        action_type = confirm_action.get("action_type")
        payload = confirm_action.get("payload", {})

        if action_type == "book_class":
            session_id = payload.get("session_id")
            class_sess = session.get(ClassSession, session_id)
            if class_sess and class_sess.gym_id == gym_id:
                booking = Booking(
                    gym_id=gym_id,
                    session_id=session_id,
                    member_id=member_id,
                    status="booked",
                )
                session.add(booking)
                session.commit()
                return {
                    "reply": "Booking confirmed! You are reserved for this session.",
                    "card": None,
                    "action_executed": True,
                }

        if action_type == "request_freeze":
            days = payload.get("days", 14)
            # Find active membership
            latest = session.exec(
                select(Membership)
                .where(Membership.gym_id == gym_id, Membership.member_id == member_id)
                .order_by(Membership.end_date.desc())
            ).first()
            if latest:
                latest.end_date = latest.end_date + timedelta(days=days)
                latest.status = "frozen"
                session.add(latest)
                session.commit()
                return {
                    "reply": f"Your membership has been frozen for {days} days. Your new renewal date is {latest.end_date.strftime('%b %d, %Y')}.",
                    "card": None,
                    "action_executed": True,
                }

    # 2. Check for intents
    # A) Book Class intent
    if "book" in q_lower or "reserve" in q_lower:
        # find upcoming session
        now = utc_now()
        session_entry = session.exec(
            select(ClassSession)
            .where(ClassSession.gym_id == gym_id, ClassSession.starts_at >= now)
            .order_by(ClassSession.starts_at.asc())
        ).first()

        if session_entry:
            cls_def = session.get(Class, session_entry.class_id)
            cls_name = cls_def.name if cls_def else "Class"
            time_str = session_entry.starts_at.strftime("%a %I:%M %p")
            return {
                "reply": f"Would you like to reserve a slot for {cls_name} on {time_str}?",
                "needs_confirmation": True,
                "confirm_card": {
                    "action_type": "book_class",
                    "title": f"Book {cls_name}",
                    "details": f"Scheduled for {time_str} in {cls_def.room if cls_def else 'Studio'}",
                    "payload": {"session_id": session_entry.id, "class_name": cls_name},
                },
            }
        else:
            return {
                "reply": "No upcoming class sessions found for booking today.",
                "needs_confirmation": False,
                "confirm_card": None,
            }

    # B) Workout plan intent
    if "workout" in q_lower or "exercise" in q_lower or "today" in q_lower:
        plan = session.exec(
            select(WorkoutPlan)
            .where(
                WorkoutPlan.gym_id == gym_id,
                WorkoutPlan.member_id == member_id,
                WorkoutPlan.status == "approved",
            )
            .order_by(WorkoutPlan.created_at.desc())
        ).first()

        if plan:
            try:
                days = json.loads(plan.days_json)
                day1 = days[0] if days else None
                if day1:
                    ex_names = [e["name"] for e in day1.get("exercises", [])]
                    return {
                        "reply": f"Your workout today is '{day1.get('title', 'Daily Session')}': {', '.join(ex_names)}. Keep good form!",
                        "needs_confirmation": False,
                        "confirm_card": None,
                    }
            except Exception:
                pass
        return {
            "reply": "You have a balanced full body workout scheduled: Bench Press, Squats, and Core Plank. Head to the weights area!",
            "needs_confirmation": False,
            "confirm_card": None,
        }

    # C) Membership & dues intent
    if "membership" in q_lower or "status" in q_lower or "renewal" in q_lower or "days left" in q_lower:
        membership = session.exec(
            select(Membership)
            .where(Membership.gym_id == gym_id, Membership.member_id == member_id)
            .order_by(Membership.end_date.desc())
        ).first()
        if membership:
            status = compute_membership_status(membership)
            days = (membership.end_date - date.today()).days
            plan = session.get(MembershipPlan, membership.plan_id)
            plan_name = plan.name if plan else "Standard"
            return {
                "reply": f"Your {plan_name} membership is currently {status.upper()} with {max(0, days)} day(s) remaining (ends {membership.end_date.strftime('%b %d, %Y')}).",
                "needs_confirmation": False,
                "confirm_card": None,
            }

    # D) Dues / payment intent
    if "due" in q_lower or "pay" in q_lower or "balance" in q_lower or "owe" in q_lower:
        dues = session.exec(
            select(Due).where(Due.gym_id == gym_id, Due.member_id == member_id, Due.status == "open")
        ).all()
        if dues:
            total = sum(d.amount_cents for d in dues)
            return {
                "reply": f"You have an outstanding balance of {format_money(total)}. You can settle this at the front desk or via online transfer.",
                "needs_confirmation": False,
                "confirm_card": None,
            }
        return {
            "reply": "Your account is in good standing with zero overdue balance!",
            "needs_confirmation": False,
            "confirm_card": None,
        }

    # E) Freeze intent
    if "freeze" in q_lower or "pause" in q_lower:
        return {
            "reply": "Would you like to freeze your membership for 14 days?",
            "needs_confirmation": True,
            "confirm_card": {
                "action_type": "request_freeze",
                "title": "Freeze Membership",
                "details": "Pause membership for 14 calendar days. Freezes will push your renewal date forward.",
                "payload": {"days": 14},
            },
        }

    # F) Hours intent
    if "hours" in q_lower or "open" in q_lower or "time" in q_lower:
        return {
            "reply": "Iron Peak Fitness is open Monday through Saturday from 5:30 AM to 10:00 PM, and Sundays from 6:00 AM to 6:00 PM.",
            "needs_confirmation": False,
            "confirm_card": None,
        }

    # Fallback via LLM
    llm = get_llm_client()
    answer = llm.generate(
        prompt=f"Member asks: '{query}'. Answer warmly as Iron Peak Fitness gym assistant.",
        system="Keep responses concise, helpful, and polite."
    )
    return {
        "reply": answer,
        "needs_confirmation": False,
        "confirm_card": None,
    }
