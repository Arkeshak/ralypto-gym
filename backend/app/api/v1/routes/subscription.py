from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.core.config import settings
from app.db.session import get_session
from app.models.gym import Gym
from app.models.user import User
from app.schemas.api import PlanSwitchRequest
from app.security.dependencies import get_current_user, require_role

router = APIRouter(prefix="/subscription", tags=["subscription"])


@router.get("/")
def get_subscription(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    gym = session.get(Gym, current_user.gym_id)
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")

    features = list(settings.PLAN_FEATURES.get(gym.plan, set()))
    limit = settings.PLAN_MEMBER_LIMITS.get(gym.plan, 150)

    plans_comparison = [
        {
            "name": "Basic",
            "price_monthly": "Rs 8,500/mo",
            "member_limit": 150,
            "features": ["Members & Check-in", "Plans & Payments", "Staff Management", "Basic Reports"],
            "ai_included": False,
        },
        {
            "name": "Standard",
            "price_monthly": "Rs 16,500/mo",
            "member_limit": 500,
            "features": ["All Basic Features", "Classes & Timetables", "Member Mobile App", "Workouts & Progress", "Crowd Live & Forecast"],
            "ai_included": False,
        },
        {
            "name": "Premium",
            "price_monthly": "Rs 28,000/mo",
            "member_limit": "Unlimited",
            "features": ["All Standard Features", "AI Churn & Win-back", "AI Workout & Meal Coach", "AI Member Voice Assistant", "AI Ask Gym Owner Intelligence", "Multi-Branch Support"],
            "ai_included": True,
        },
    ]

    return {
        "current_plan": gym.plan,
        "plan_status": gym.plan_status,
        "renews_at": gym.plan_renews_at.isoformat() if gym.plan_renews_at else "2026-11-26",
        "member_limit": limit,
        "features": features,
        "plans": plans_comparison,
        "dev_tools_enabled": settings.VITE_DEV_TOOLS,
    }


@router.post("/dev-switch-plan")
def dev_switch_plan(
    req: PlanSwitchRequest,
    current_user: User = Depends(require_role(["owner"])),
    session: Session = Depends(get_session),
):
    if not settings.VITE_DEV_TOOLS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "PROD_RESTRICTED", "message": "Plan switcher is disabled in production environments."},
        )

    if req.plan not in ["Basic", "Standard", "Premium"]:
        raise HTTPException(status_code=400, detail="Invalid plan name. Choose Basic, Standard, or Premium.")

    gym = session.get(Gym, current_user.gym_id)
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")

    gym.plan = req.plan
    session.add(gym)
    session.commit()
    session.refresh(gym)

    return {
        "status": "plan_switched",
        "new_plan": gym.plan,
        "features": list(settings.PLAN_FEATURES.get(gym.plan, set())),
    }
