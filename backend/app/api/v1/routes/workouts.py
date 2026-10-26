from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.base import utc_now
from app.models.member import Member
from app.models.user import User
from app.models.workout import Exercise, MealPlan, WorkoutLog, WorkoutPlan
from app.schemas.api import ExerciseCreate, WorkoutLogCreate
from app.security.dependencies import get_current_user, require_feature, require_role

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.get("/exercises")
def list_exercises(
    muscle_group: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    _gym=Depends(require_feature("workouts")),
    session: Session = Depends(get_session),
):
    query = select(Exercise).where(Exercise.gym_id == current_user.gym_id)
    if muscle_group:
        query = query.where(Exercise.muscle_group == muscle_group)
    return session.exec(query).all()


@router.post("/exercises", status_code=status.HTTP_201_CREATED)
def create_exercise(
    req: ExerciseCreate,
    current_user: User = Depends(require_role(["owner", "manager", "trainer"])),
    _gym=Depends(require_feature("workouts")),
    session: Session = Depends(get_session),
):
    ex = Exercise(
        gym_id=current_user.gym_id,
        name=req.name,
        muscle_group=req.muscle_group,
        equipment=req.equipment,
        level=req.level,
        how_to=req.how_to,
        media_url=req.media_url,
        contraindications_json=req.contraindications_json,
    )
    session.add(ex)
    session.commit()
    session.refresh(ex)
    return ex


@router.get("/plans")
def list_workout_plans(
    member_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    _gym=Depends(require_feature("workouts")),
    session: Session = Depends(get_session),
):
    target_member = member_id or (current_user.linked_member_id if current_user.role == "member" else None)
    query = select(WorkoutPlan).where(WorkoutPlan.gym_id == current_user.gym_id)
    if target_member:
        query = query.where(WorkoutPlan.member_id == target_member)
    if status_filter:
        query = query.where(WorkoutPlan.status == status_filter)
    return session.exec(query.order_by(WorkoutPlan.created_at.desc())).all()


@router.post("/plans/{id}/approve")
def approve_plan(
    id: str,
    current_user: User = Depends(require_role(["owner", "manager", "trainer"])),
    _gym=Depends(require_feature("workouts")),
    session: Session = Depends(get_session),
):
    plan = session.get(WorkoutPlan, id)
    if not plan or plan.gym_id != current_user.gym_id:
        raise HTTPException(status_code=404, detail="Plan not found")

    plan.status = "approved"
    plan.approved_by = current_user.name
    plan.approved_at = utc_now()
    plan.updated_at = utc_now()

    session.add(plan)
    session.commit()
    session.refresh(plan)
    return {"status": "approved", "plan_id": plan.id}


@router.post("/logs")
def log_workout(
    req: WorkoutLogCreate,
    current_user: User = Depends(get_current_user),
    _gym=Depends(require_feature("workouts")),
    session: Session = Depends(get_session),
):
    member_id = req.member_id or current_user.linked_member_id or current_user.id
    log = WorkoutLog(
        gym_id=current_user.gym_id,
        member_id=member_id,
        exercise_id=req.exercise_id,
        plan_id=req.plan_id,
        date=req.date,
        sets_json=req.sets_json,
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


@router.get("/meal-plans")
def list_meal_plans(
    member_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    _gym=Depends(require_feature("workouts")),
    session: Session = Depends(get_session),
):
    query = select(MealPlan).where(MealPlan.gym_id == current_user.gym_id)
    if member_id:
        query = query.where(MealPlan.member_id == member_id)
    return session.exec(query.order_by(MealPlan.created_at.desc())).all()
