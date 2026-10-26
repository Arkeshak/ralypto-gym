import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from app.ai.features.ask_gym import execute_ask_gym
from app.ai.features.assistant import handle_assistant_query
from app.ai.features.churn import compute_all_churn_scores, draft_winback_message
from app.ai.features.coach import generate_ai_meal_plan, generate_ai_workout_plan
from app.ai.features.crowd import get_crowd_forecast
from app.ai.features.weekly_summary import (
    generate_weekly_summary,
    send_weekly_summary_to_owner,
)
from app.db.session import get_session
from app.models.ai import AIAction, ChurnScore
from app.models.member import Member
from app.models.user import User
from app.schemas.api import (
    AskGymRequest,
    AssistantChatRequest,
    CoachPlanRequest,
    WinbackDraftRequest,
)
from app.security.dependencies import get_current_user, require_feature, require_role

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/churn-risk")
def get_churn_risk_list(
    trainer_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    _gym=Depends(require_feature("churn_rules")),
    session: Session = Depends(get_session),
):
    gym_id = current_user.gym_id
    query = (
        select(ChurnScore, Member)
        .join(Member, Member.id == ChurnScore.member_id)
        .where(ChurnScore.gym_id == gym_id, Member.deleted == False)
        .order_by(ChurnScore.score.desc())
    )
    if trainer_id:
        query = query.where(Member.trainer_id == trainer_id)

    results = session.exec(query).all()

    items = []
    for score_record, member in results:
        items.append({
            "member_id": member.id,
            "member_code": member.member_code,
            "name": member.name,
            "phone": member.phone,
            "score": score_record.score,
            "level": score_record.level,
            "reasons": json.loads(score_record.reasons_json),
            "computed_at": score_record.computed_at.isoformat(),
        })
    return items


@router.post("/recompute-churn")
def recompute_churn(
    current_user: User = Depends(require_role(["owner", "manager"])),
    _gym=Depends(require_feature("churn_rules")),
    session: Session = Depends(get_session),
):
    scores = compute_all_churn_scores(session=session, gym_id=current_user.gym_id)
    return {"status": "recomputed", "count": len(scores)}


@router.post("/winback-draft")
def create_winback_draft(
    req: WinbackDraftRequest,
    current_user: User = Depends(require_role(["owner", "manager", "front_desk"])),
    _gym=Depends(require_feature("winback_agent")),
    session: Session = Depends(get_session),
):
    return draft_winback_message(
        session=session,
        gym_id=current_user.gym_id,
        member_id=req.member_id,
        offer=req.offer,
        user_id=current_user.id,
    )


@router.post("/coach/plan")
def create_coach_plan(
    req: CoachPlanRequest,
    current_user: User = Depends(get_current_user),
    _gym=Depends(require_feature("ai_coach")),
    session: Session = Depends(get_session),
):
    target_member = req.member_id or current_user.linked_member_id or current_user.id
    plan = generate_ai_workout_plan(
        session=session,
        gym_id=current_user.gym_id,
        member_id=target_member,
        goal=req.goal,
        level=req.level,
        days_per_week=req.days_per_week,
        user_id=current_user.id,
    )
    return {
        "plan_id": plan.id,
        "title": plan.title,
        "status": plan.status,
        "days": json.loads(plan.days_json),
        "notes": plan.notes,
    }


@router.post("/coach/meal")
def create_coach_meal(
    member_id: str,
    dietary_pref: str = "non-vegetarian",
    current_user: User = Depends(get_current_user),
    _gym=Depends(require_feature("ai_coach")),
    session: Session = Depends(get_session),
):
    target_member = member_id or current_user.linked_member_id or current_user.id
    meal = generate_ai_meal_plan(
        session=session,
        gym_id=current_user.gym_id,
        member_id=target_member,
        dietary_pref=dietary_pref,
        user_id=current_user.id,
    )
    return {
        "meal_plan_id": meal.id,
        "title": meal.title,
        "status": meal.status,
        "days": json.loads(meal.days_json),
        "notes": meal.notes,
    }


@router.post("/assistant/chat")
def assistant_chat(
    req: AssistantChatRequest,
    current_user: User = Depends(get_current_user),
    _gym=Depends(require_feature("ai_assistant")),
    session: Session = Depends(get_session),
):
    member_id = current_user.linked_member_id or current_user.id
    return handle_assistant_query(
        session=session,
        gym_id=current_user.gym_id,
        member_id=member_id,
        query=req.query,
        confirm_action=req.confirm_action,
        user_id=current_user.id,
    )


@router.get("/crowd-forecast")
def crowd_forecast(
    current_user: User = Depends(get_current_user),
    _gym=Depends(require_feature("crowd")),
    session: Session = Depends(get_session),
):
    return get_crowd_forecast(session=session, gym_id=current_user.gym_id)


@router.post("/ask-gym")
def ask_gym_query(
    req: AskGymRequest,
    current_user: User = Depends(require_role(["owner", "manager"])),
    _gym=Depends(require_feature("ask_gym")),
    session: Session = Depends(get_session),
):
    return execute_ask_gym(
        session=session,
        gym_id=current_user.gym_id,
        query=req.query,
        user_id=current_user.id,
    )


@router.get("/weekly-summary")
def get_weekly_summary(
    current_user: User = Depends(require_role(["owner", "manager"])),
    _gym=Depends(require_feature("weekly_summary")),
    session: Session = Depends(get_session),
):
    return generate_weekly_summary(
        session=session,
        gym_id=current_user.gym_id,
        user_id=current_user.id,
    )


@router.post("/weekly-summary/send")
def send_weekly_summary(
    current_user: User = Depends(require_role(["owner"])),
    _gym=Depends(require_feature("weekly_summary")),
    session: Session = Depends(get_session),
):
    return send_weekly_summary_to_owner(
        session=session,
        gym_id=current_user.gym_id,
        user_id=current_user.id,
    )


@router.get("/actions")
def list_ai_actions(
    limit: int = Query(default=30, ge=1, le=100),
    current_user: User = Depends(require_role(["owner", "manager"])),
    session: Session = Depends(get_session),
):
    actions = session.exec(
        select(AIAction)
        .where(AIAction.gym_id == current_user.gym_id)
        .order_by(AIAction.created_at.desc())
        .limit(limit)
    ).all()

    return [
        {
            "id": a.id,
            "feature": a.feature,
            "tool": a.tool,
            "status": a.status,
            "input": json.loads(a.input_json),
            "output": json.loads(a.output_json),
            "created_at": a.created_at.isoformat(),
        }
        for a in actions
    ]
