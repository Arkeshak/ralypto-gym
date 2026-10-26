from datetime import date, timedelta
import pytest
from fastapi import HTTPException
from sqlmodel import Session
from app.models.member import Member
from app.models.plan import Membership
from app.security.jwt import create_qr_token
from app.services.checkin_service import (
    get_live_attendance,
    process_checkin,
    process_checkout,
)


def test_checkin_active_member_returns_ok(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    plan_a = seed_tenants["plan_a"]

    m = Member(gym_id=gym_a.id, member_code="IPF-3001", name="Active Checkin", phone="+94 77 111 2222")
    session.add(m)
    session.commit()

    today = date.today()
    ms = Membership(
        gym_id=gym_a.id,
        member_id=m.id,
        plan_id=plan_a.id,
        start_date=today - timedelta(days=5),
        end_date=today + timedelta(days=25),
        status="active",
    )
    session.add(ms)
    session.commit()

    res = process_checkin(session, gym_a.id, m.member_code)
    assert res["result"] == "ok"
    assert res["blocked_reason"] is None
    assert res["member"]["status"] == "active"


def test_checkin_expired_member_returns_blocked_with_reason(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    plan_a = seed_tenants["plan_a"]

    m = Member(gym_id=gym_a.id, member_code="IPF-3002", name="Expired Checkin", phone="+94 77 333 4444")
    session.add(m)
    session.commit()

    today = date.today()
    ms = Membership(
        gym_id=gym_a.id,
        member_id=m.id,
        plan_id=plan_a.id,
        start_date=today - timedelta(days=60),
        end_date=today - timedelta(days=20),
        status="expired",
    )
    session.add(ms)
    session.commit()

    res = process_checkin(session, gym_a.id, m.member_code)
    assert res["result"] == "blocked"
    assert "expired" in res["blocked_reason"].lower()
    assert res["member"]["status"] == "expired"


def test_checkin_frozen_member_returns_blocked(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    plan_a = seed_tenants["plan_a"]

    m = Member(gym_id=gym_a.id, member_code="IPF-3003", name="Frozen Checkin", phone="+94 77 555 6666")
    session.add(m)
    session.commit()

    today = date.today()
    ms = Membership(
        gym_id=gym_a.id,
        member_id=m.id,
        plan_id=plan_a.id,
        start_date=today - timedelta(days=5),
        end_date=today + timedelta(days=25),
        status="frozen",
    )
    session.add(ms)
    session.commit()

    res = process_checkin(session, gym_a.id, m.member_code)
    assert res["result"] == "blocked"
    assert "frozen" in res["blocked_reason"].lower()


def test_checkin_grace_member_returns_ok_with_warning(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    plan_a = seed_tenants["plan_a"]

    m = Member(gym_id=gym_a.id, member_code="IPF-3004", name="Grace Checkin", phone="+94 77 777 8888")
    session.add(m)
    session.commit()

    today = date.today()
    ms = Membership(
        gym_id=gym_a.id,
        member_id=m.id,
        plan_id=plan_a.id,
        start_date=today - timedelta(days=35),
        end_date=today - timedelta(days=3),  # ended 3 days ago, grace is 7 days
        status="active",
    )
    session.add(ms)
    session.commit()

    res = process_checkin(session, gym_a.id, m.member_code)
    assert res["result"] == "ok"
    assert "grace" in res["blocked_reason"].lower()
    assert res["member"]["status"] == "grace"


def test_checkin_with_phone_number(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    m = Member(gym_id=gym_a.id, member_code="IPF-3005", name="Phone Member", phone="+94 71 888 9999")
    session.add(m)
    session.commit()

    res = process_checkin(session, gym_a.id, identifier="+94 71 888 9999", method="phone")
    assert res["member"]["id"] == m.id


def test_checkin_with_valid_qr_token(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    plan_a = seed_tenants["plan_a"]

    m = Member(gym_id=gym_a.id, member_code="IPF-3006", name="QR Member", phone="+94 77 000 1234")
    session.add(m)
    session.commit()

    today = date.today()
    ms = Membership(
        gym_id=gym_a.id,
        member_id=m.id,
        plan_id=plan_a.id,
        start_date=today,
        end_date=today + timedelta(days=30),
        status="active",
    )
    session.add(ms)
    session.commit()

    valid_token = create_qr_token(gym_id=gym_a.id, member_id=m.id, expires_seconds=60)
    res = process_checkin(session, gym_a.id, identifier=valid_token, method="qr")
    assert res["result"] == "ok"
    assert res["member"]["id"] == m.id


def test_checkin_with_expired_qr_token_fails(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    m = Member(gym_id=gym_a.id, member_code="IPF-3007", name="Expired QR Member", phone="+94 77 000 5678")
    session.add(m)
    session.commit()

    # Expired token (-10 seconds)
    expired_token = create_qr_token(gym_id=gym_a.id, member_id=m.id, expires_seconds=-10)

    # Should fall back to code search, fail to find member by token string, and raise 404
    with pytest.raises(HTTPException) as exc:
        process_checkin(session, gym_a.id, identifier=expired_token, method="qr")
    assert exc.value.status_code == 404


def test_checkin_with_wrong_gym_qr_token_rejected(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    gym_b = seed_tenants["gym_b"]

    m_b = Member(gym_id=gym_b.id, member_code="CFC-3008", name="Gym B Member", phone="+94 77 000 9999")
    session.add(m_b)
    session.commit()

    token_b = create_qr_token(gym_id=gym_b.id, member_id=m_b.id, expires_seconds=60)

    # Scanned at Gym A
    with pytest.raises(HTTPException) as exc:
        process_checkin(session, gym_a.id, identifier=token_b, method="qr")
    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "WRONG_GYM"


def test_live_occupancy_counter_and_checkout(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    plan_a = seed_tenants["plan_a"]
    m = Member(gym_id=gym_a.id, member_code="IPF-3009", name="Live Member", phone="+94 77 121 2121")
    session.add(m)
    session.commit()

    today = date.today()
    ms = Membership(
        gym_id=gym_a.id,
        member_id=m.id,
        plan_id=plan_a.id,
        start_date=today,
        end_date=today + timedelta(days=30),
        status="active",
    )
    session.add(ms)
    session.commit()

    checkin_res = process_checkin(session, gym_a.id, m.member_code)
    live_before = get_live_attendance(session, gym_a.id)
    assert live_before["live_count"] >= 1

    process_checkout(session, checkin_res["checkin_id"], gym_a.id)
    live_after = get_live_attendance(session, gym_a.id)
    assert live_after["live_count"] == live_before["live_count"] - 1
