from datetime import timedelta
import json
import pytest
from sqlmodel import Session, select
from app.ai.clients.mock_client import MockLLM
from app.ai.features.ask_gym import execute_ask_gym
from app.ai.features.assistant import handle_assistant_query
from app.ai.features.churn import compute_member_churn, draft_winback_message
from app.ai.features.coach import (
    approve_workout_plan,
    generate_ai_meal_plan,
    generate_ai_workout_plan,
)
from app.ai.features.crowd import get_crowd_forecast
from app.ai.features.weekly_summary import generate_weekly_summary
from app.models.ai import AIAction
from app.models.class_model import Booking, Class, ClassSession
from app.models.member import HealthForm, Member
from app.models.workout import Exercise, WorkoutPlan
from app.models.base import utc_now


def test_mock_llm_deterministic_output():
    client = MockLLM()
    res = client.generate("Generate workout plan from exercise library")
    data = json.loads(res)
    assert "days" in data
    assert len(data["days"]) > 0

    res_si = client.generate("Draft a warm winback message in sinhala")
    assert "ආයුබෝවන්" in res_si


def test_churn_calculation_rules_and_reasons(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    m = Member(gym_id=gym_a.id, member_code="IPF-C1", name="Churn Member", phone="+94 77 111 3333")
    session.add(m)
    session.commit()

    churn = compute_member_churn(session, m, gym_a.id)
    assert 0 <= churn.score <= 100
    assert churn.level in ["High", "Medium", "Low"]
    reasons = json.loads(churn.reasons_json)
    assert isinstance(reasons, list)


def test_winback_draft_message_generation_and_logging(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    owner_a = seed_tenants["owner_a"]
    m = Member(gym_id=gym_a.id, member_code="IPF-C2", name="Winback Target", phone="+94 77 222 4444")
    session.add(m)
    session.commit()

    draft = draft_winback_message(session, gym_a.id, m.id, offer="20% off", user_id=owner_a.id)
    assert "message_id" in draft
    assert draft["status"] == "draft"
    assert "https://wa.me/94772224444" in draft["whatsapp_url"]

    # Verify logged in ai_actions
    action = session.exec(select(AIAction).where(AIAction.gym_id == gym_a.id, AIAction.feature == "winback_agent")).first()
    assert action is not None


def test_ai_coach_workout_plan_pending_approval(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    owner_a = seed_tenants["owner_a"]
    m = Member(gym_id=gym_a.id, member_code="IPF-C3", name="Coach Member", phone="+94 77 333 5555")
    session.add(m)
    session.commit()

    plan = generate_ai_workout_plan(session, gym_a.id, m.id, goal="Hypertrophy", days_per_week=3, user_id=owner_a.id)
    assert plan.status == "pending_approval"
    assert plan.source == "ai"
    assert "General fitness guidance" in plan.notes


def test_ai_coach_excludes_injuries_contraindications(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    m = Member(gym_id=gym_a.id, member_code="IPF-C4", name="Injured Member", phone="+94 77 444 6666")
    session.add(m)

    hf = HealthForm(gym_id=gym_a.id, member_id=m.id, flagged=True, injuries="Severe knee pain")
    session.add(hf)
    session.commit()

    plan = generate_ai_workout_plan(session, gym_a.id, m.id, goal="General fitness", days_per_week=2)
    assert plan.status == "pending_approval"
    assert "Flagged" in plan.notes


def test_ai_coach_approval_workflow(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    trainer_a = seed_tenants["trainer_a"]
    m = Member(gym_id=gym_a.id, member_code="IPF-C5", name="Approve Member", phone="+94 77 555 7777")
    session.add(m)
    session.commit()

    plan = generate_ai_workout_plan(session, gym_a.id, m.id, goal="Tone up")
    assert plan.status == "pending_approval"

    approved = approve_workout_plan(session, plan.id, gym_a.id, trainer_id=trainer_a.id)
    assert approved.status == "approved"
    assert approved.approved_by == trainer_a.id


def test_ai_coach_meal_plan_generation(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    m = Member(gym_id=gym_a.id, member_code="IPF-C6", name="Meal Member", phone="+94 77 666 8888")
    session.add(m)
    session.commit()

    meal = generate_ai_meal_plan(session, gym_a.id, m.id, dietary_pref="vegetarian")
    assert meal.status == "pending_approval"
    assert "Plan" in meal.title


def test_assistant_confirm_card_workflow_for_booking(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    m = Member(gym_id=gym_a.id, member_code="IPF-C7", name="Assistant Member", phone="+94 77 777 9999")
    session.add(m)

    # Class and session
    c = Class(gym_id=gym_a.id, name="Zumba", room="Studio A", capacity=20)
    session.add(c)
    session.commit()
    session.refresh(c)

    sess = ClassSession(gym_id=gym_a.id, class_id=c.id, starts_at=utc_now() + timedelta(hours=2), capacity=20)
    session.add(sess)
    session.commit()

    # Step 1: Member asks to book
    step1 = handle_assistant_query(session, gym_a.id, m.id, query="Book me Zumba class")
    assert step1["needs_confirmation"] is True
    assert step1["confirm_card"]["action_type"] == "book_class"

    # Step 2: Member taps confirm
    step2 = handle_assistant_query(
        session,
        gym_id=gym_a.id,
        member_id=m.id,
        query="",
        confirm_action={
            "confirmed": True,
            "action_type": "book_class",
            "payload": {"session_id": sess.id},
        },
    )
    assert step2["action_executed"] is True
    assert "confirmed" in step2["reply"].lower()

    # Verify booking in db
    b = session.exec(select(Booking).where(Booking.session_id == sess.id, Booking.member_id == m.id)).first()
    assert b is not None
    assert b.status == "booked"


def test_crowd_forecast_shape_and_distribution(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    fc = get_crowd_forecast(session, gym_a.id)

    assert "live_count" in fc
    assert "current_status" in fc
    assert "best_time_to_go" in fc
    assert len(fc["hourly_distribution"]) == 17  # hours 6 to 22


def test_ask_gym_safe_analytical_query(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    owner_a = seed_tenants["owner_a"]

    res_rev = execute_ask_gym(session, gym_a.id, query="How is revenue vs last month?", user_id=owner_a.id)
    assert "revenue" in res_rev["answer"].lower()
    assert res_rev["chart_data"] is not None
    assert res_rev["tool_used"] == "revenue_summary"

    res_risk = execute_ask_gym(session, gym_a.id, query="How many members are at risk?", user_id=owner_a.id)
    assert "risk" in res_risk["answer"].lower()
    assert res_risk["tool_used"] == "churn_risk_summary"


def test_weekly_summary_generation(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    owner_a = seed_tenants["owner_a"]

    summary = generate_weekly_summary(session, gym_a.id, user_id=owner_a.id)
    assert "metrics" in summary
    assert "tips" in summary
    assert len(summary["tips"]) >= 2
    assert "summary_text" in summary
