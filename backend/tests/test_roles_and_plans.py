import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.core.config import settings
from app.models.member import Member
from app.security.jwt import create_access_token
from app.services.membership_service import check_member_limit


def test_front_desk_blocked_from_staff_management(client: TestClient, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    frontdesk = seed_tenants["frontdesk_a"]

    token = create_access_token({"sub": frontdesk.id, "gym_id": gym_a.id, "role": frontdesk.role})
    res = client.get("/api/v1/staff/", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    assert res.json()["code"] == "FORBIDDEN"


def test_trainer_blocked_from_daily_cash_summary(client: TestClient, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    trainer = seed_tenants["trainer_a"]

    token = create_access_token({"sub": trainer.id, "gym_id": gym_a.id, "role": trainer.role})
    res = client.get("/api/v1/payments/daily-summary", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    assert res.json()["code"] == "FORBIDDEN"


def test_owner_role_can_access_all(client: TestClient, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    owner = seed_tenants["owner_a"]

    token = create_access_token({"sub": owner.id, "gym_id": gym_a.id, "role": owner.role})
    res_staff = client.get("/api/v1/staff/", headers={"Authorization": f"Bearer {token}"})
    assert res_staff.status_code == 200

    res_cash = client.get("/api/v1/payments/daily-summary", headers={"Authorization": f"Bearer {token}"})
    assert res_cash.status_code == 200


def test_basic_plan_blocked_from_ai_features(client: TestClient, seed_tenants):
    gym_b = seed_tenants["gym_b"]  # Basic plan
    owner_b = seed_tenants["owner_b"]

    token = create_access_token({"sub": owner_b.id, "gym_id": gym_b.id, "role": owner_b.role})
    res = client.post("/api/v1/ai/ask-gym", json={"query": "How is revenue?"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    assert res.json()["code"] == "FEATURE_LOCKED"
    assert "upgrade" in res.json()["message"].lower()


def test_basic_plan_blocked_from_classes(client: TestClient, seed_tenants):
    gym_b = seed_tenants["gym_b"]
    owner_b = seed_tenants["owner_b"]

    token = create_access_token({"sub": owner_b.id, "gym_id": gym_b.id, "role": owner_b.role})
    res = client.get("/api/v1/classes/", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    assert res.json()["code"] == "FEATURE_LOCKED"


def test_premium_plan_allowed_ai_and_classes(client: TestClient, seed_tenants):
    gym_a = seed_tenants["gym_a"]  # Premium plan
    owner_a = seed_tenants["owner_a"]

    token = create_access_token({"sub": owner_a.id, "gym_id": gym_a.id, "role": owner_a.role})
    res_classes = client.get("/api/v1/classes/", headers={"Authorization": f"Bearer {token}"})
    assert res_classes.status_code == 200

    res_ai = client.post("/api/v1/ai/ask-gym", json={"query": "How is revenue?"}, headers={"Authorization": f"Bearer {token}"})
    assert res_ai.status_code == 200


def test_unauthenticated_request_rejected_with_401(client: TestClient):
    res = client.get("/api/v1/members/")
    assert res.status_code == 401
    assert res.json()["code"] == "UNAUTHORIZED"


def test_pin_login_endpoint(client: TestClient, seed_tenants):
    res = client.post("/api/v1/auth/pin-login", json={"gym_code": "IPF", "pin": "1234"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "front_desk"


def test_member_limit_enforcement(session: Session, seed_tenants):
    gym_b = seed_tenants["gym_b"]
    gym_b.plan = "Basic"
    session.add(gym_b)
    session.commit()

    # Add 150 members
    for i in range(150):
        session.add(Member(gym_id=gym_b.id, member_code=f"LIM-{i}", name=f"Limit {i}", phone=f"+94 77 100 {i:04d}"))
    session.commit()

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        check_member_limit(session, gym_b.id)
    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "MEMBER_LIMIT_REACHED"
