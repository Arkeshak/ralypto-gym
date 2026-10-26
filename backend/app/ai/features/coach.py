from datetime import datetime
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from app.ai.clients.factory import get_llm_client
from app.models.ai import AIAction
from app.models.base import utc_now
from app.models.member import HealthForm, Member
from app.models.workout import Exercise, MealPlan, WorkoutPlan


class ExerciseItemSchema(BaseModel):
    exercise_id: str
    name: str
    sets: int = 3
    reps: int = 10
    rest_sec: int = 60
    notes: Optional[str] = None


class WorkoutDaySchema(BaseModel):
    day_number: int
    title: str
    exercises: List[ExerciseItemSchema]


class WorkoutPlanSchema(BaseModel):
    title: str
    days: List[WorkoutDaySchema]
    notes: str


def generate_ai_workout_plan(
    session: Session,
    gym_id: str,
    member_id: str,
    goal: str,
    level: str = "beginner",
    days_per_week: int = 3,
    user_id: Optional[str] = None,
) -> WorkoutPlan:
    member = session.get(Member, member_id)
    if not member or member.gym_id != gym_id:
        raise ValueError("Member not found")

    # Check health form for injuries or flags
    health_form = session.exec(
        select(HealthForm).where(
            HealthForm.gym_id == gym_id,
            HealthForm.member_id == member_id,
        )
    ).first()

    has_injuries = bool(health_form and (health_form.flagged or health_form.injuries))

    # Fetch available exercises in gym library
    exercises = session.exec(
        select(Exercise).where(Exercise.gym_id == gym_id)
    ).all()

    # Filter out contra-indicated exercises if injury is noted
    safe_exercises = []
    for ex in exercises:
        if has_injuries and "knee_pain" in ex.contraindications_json and "squat" in ex.name.lower():
            continue
        safe_exercises.append(ex)

    if not safe_exercises:
        safe_exercises = exercises

    prompt = (
        f"Generate a {days_per_week}-day workout plan for gym member {member.name}. "
        f"Goal: {goal}, Level: {level}, Has injuries: {has_injuries}. "
        f"Available exercises: {[e.name for e in safe_exercises[:15]]}. "
        "Return valid JSON matching title, days (day_number, title, exercises), and notes."
    )

    llm = get_llm_client()
    raw_response = llm.generate(prompt=prompt, system="You are an expert fitness coach.")

    try:
        data = json.loads(raw_response)
        plan_parsed = WorkoutPlanSchema(**data)
        days_json = json.dumps([d.model_dump() for d in plan_parsed.days])
        title = plan_parsed.title
        notes = plan_parsed.notes
    except Exception:
        # Fallback to deterministic template
        title = f"{days_per_week}-Day Customized Fitness Blueprint"
        days_list = []
        for i in range(1, min(days_per_week + 1, 4)):
            slice_start = (i - 1) * 3
            day_exs = safe_exercises[slice_start : slice_start + 3] or safe_exercises[:3]
            days_list.append({
                "day_number": i,
                "title": f"Session {i}: Foundation Circuit",
                "exercises": [
                    {
                        "exercise_id": e.id,
                        "name": e.name,
                        "sets": 3,
                        "reps": 12 if level == "beginner" else 10,
                        "rest_sec": 60,
                        "notes": "Controlled tempo; maintain strict form.",
                    }
                    for e in day_exs
                ],
            })
        days_json = json.dumps(days_list)
        notes = "General fitness guidance. Talk to a doctor if you have health problems."

    if has_injuries:
        notes += " [Flagged: Member noted health limits. Coach review mandatory before heavy loading.]"

    # Save plan with pending_approval status
    workout_plan = WorkoutPlan(
        gym_id=gym_id,
        member_id=member_id,
        created_by=user_id or "AI Coach",
        source="ai",
        status="pending_approval",
        title=title,
        days_json=days_json,
        notes=notes,
    )
    session.add(workout_plan)

    action = AIAction(
        gym_id=gym_id,
        user_id=user_id,
        feature="ai_coach",
        tool="generate_workout_plan",
        input_json=json.dumps({"member_id": member_id, "goal": goal, "level": level}),
        output_json=json.dumps({"plan_id": workout_plan.id, "title": title}),
        status="completed",
    )
    session.add(action)
    session.commit()
    session.refresh(workout_plan)
    return workout_plan


def generate_ai_meal_plan(
    session: Session,
    gym_id: str,
    member_id: str,
    dietary_pref: str = "non-vegetarian",
    budget: str = "moderate",
    user_id: Optional[str] = None,
) -> MealPlan:
    member = session.get(Member, member_id)
    if not member or member.gym_id != gym_id:
        raise ValueError("Member not found")

    prompt = (
        f"Generate a 1-day sample Sri Lankan healthy meal plan for member {member.name}. "
        f"Preference: {dietary_pref}, Budget: {budget}. Include local ingredients like eggs, dhal, rice, fish/vegetables."
    )

    llm = get_llm_client()
    raw = llm.generate(prompt=prompt, system="You are a sports nutritionist specializing in Sri Lankan cuisine.")

    try:
        data = json.loads(raw)
        title = data.get("title", "Sri Lankan High-Protein Balance Plan")
        days_json = json.dumps(data.get("days", []))
        notes = data.get("notes", "General nutrition advice. Not medical guidance.")
    except Exception:
        title = "Sri Lankan Nutrition Balance Plan"
        days_json = json.dumps([
            {
                "day_number": 1,
                "meals": [
                    {"name": "Breakfast", "items": "2 boiled eggs, string hoppers with dhal curry and pol sambol"},
                    {"name": "Mid-morning", "items": "Fresh banana or papaya slices with green tea"},
                    {"name": "Lunch", "items": "Red rice (1 cup), steamed fish or soya meat, gotukola sambol, dhal"},
                    {"name": "Evening snack", "items": "Boiled chickpeas (kadala) with grated coconut"},
                    {"name": "Dinner", "items": "Grilled chicken breast or egg curry with steamed vegetables"},
                ],
            }
        ])
        notes = "General fitness guidance. Hydrate with at least 2.5L water daily."

    meal_plan = MealPlan(
        gym_id=gym_id,
        member_id=member_id,
        created_by=user_id or "AI Coach",
        source="ai",
        status="pending_approval",
        title=title,
        days_json=days_json,
        notes=notes,
    )
    session.add(meal_plan)

    action = AIAction(
        gym_id=gym_id,
        user_id=user_id,
        feature="ai_coach",
        tool="generate_meal_plan",
        input_json=json.dumps({"member_id": member_id, "dietary_pref": dietary_pref}),
        output_json=json.dumps({"meal_plan_id": meal_plan.id, "title": title}),
        status="completed",
    )
    session.add(action)
    session.commit()
    session.refresh(meal_plan)
    return meal_plan


def approve_workout_plan(
    session: Session,
    plan_id: str,
    gym_id: str,
    trainer_id: str,
) -> WorkoutPlan:
    plan = session.get(WorkoutPlan, plan_id)
    if not plan or plan.gym_id != gym_id:
        raise ValueError("Plan not found")

    plan.status = "approved"
    plan.approved_by = trainer_id
    plan.approved_at = utc_now()
    plan.updated_at = utc_now()

    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan
