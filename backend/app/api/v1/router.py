from fastapi import APIRouter
from app.api.v1.routes import (
    ai,
    auth,
    checkin,
    classes,
    crm,
    members,
    payments,
    plans,
    reports,
    staff,
    subscription,
    workouts,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(members.router)
api_router.include_router(plans.router)
api_router.include_router(payments.router)
api_router.include_router(checkin.router)
api_router.include_router(classes.router)
api_router.include_router(workouts.router)
api_router.include_router(crm.router)
api_router.include_router(staff.router)
api_router.include_router(reports.router)
api_router.include_router(subscription.router)
api_router.include_router(ai.router)
