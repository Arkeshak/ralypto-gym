import pytest
from datetime import date, timedelta
from fastapi import HTTPException
from sqlmodel import Session
from app.models.plan import Membership
from app.services.membership_service import (
    compute_membership_status,
    format_money,
    freeze_membership,
    renew_or_create_membership,
)


def test_status_active_when_well_within_dates():
    today = date(2026, 10, 26)
    ms = Membership(
        gym_id="g1",
        member_id="m1",
        plan_id="p1",
        start_date=date(2026, 10, 1),
        end_date=date(2026, 11, 15),
        status="active",
    )
    assert compute_membership_status(ms, grace_days=7, as_of=today) == "active"


def test_status_expiring_within_7_days():
    today = date(2026, 10, 26)
    ms = Membership(
        gym_id="g1",
        member_id="m1",
        plan_id="p1",
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 30),  # 4 days away
        status="active",
    )
    assert compute_membership_status(ms, grace_days=7, as_of=today) == "expiring"


def test_status_grace_when_ended_within_grace_days():
    today = date(2026, 10, 26)
    ms = Membership(
        gym_id="g1",
        member_id="m1",
        plan_id="p1",
        start_date=date(2026, 9, 20),
        end_date=date(2026, 10, 22),  # ended 4 days ago
        status="active",
    )
    assert compute_membership_status(ms, grace_days=7, as_of=today) == "grace"


def test_status_expired_when_past_grace_period():
    today = date(2026, 10, 26)
    ms = Membership(
        gym_id="g1",
        member_id="m1",
        plan_id="p1",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 10, 10),  # ended 16 days ago
        status="active",
    )
    assert compute_membership_status(ms, grace_days=7, as_of=today) == "expired"


def test_status_frozen_flag():
    today = date(2026, 10, 26)
    ms = Membership(
        gym_id="g1",
        member_id="m1",
        plan_id="p1",
        start_date=date(2026, 10, 1),
        end_date=date(2026, 11, 1),
        status="frozen",
    )
    assert compute_membership_status(ms, grace_days=7, as_of=today) == "frozen"


def test_status_none_membership_returns_expired():
    assert compute_membership_status(None) == "expired"


def test_format_money_lkr():
    assert format_money(500000) == "Rs 5,000"
    assert format_money(80000) == "Rs 800"
    assert format_money(1350000) == "Rs 13,500"
    assert format_money(1250) == "Rs 12.50"


def test_renewal_extends_from_future_end_date(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    plan_a = seed_tenants["plan_a"]

    # Initial membership ending in 10 days
    today = date.today()
    initial_ms = Membership(
        gym_id=gym_a.id,
        member_id="m_renew_1",
        plan_id=plan_a.id,
        start_date=today - timedelta(days=20),
        end_date=today + timedelta(days=10),
        status="active",
    )
    session.add(initial_ms)
    session.commit()

    renewed = renew_or_create_membership(session, "m_renew_1", plan_a.id, gym_a.id)
    # Should start the day after current end date
    assert renewed.start_date == initial_ms.end_date + timedelta(days=1)
    assert renewed.end_date == renewed.start_date + timedelta(days=plan_a.duration_days)


def test_renewal_starts_today_when_already_expired(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    plan_a = seed_tenants["plan_a"]

    # Expired 20 days ago
    today = date.today()
    old_ms = Membership(
        gym_id=gym_a.id,
        member_id="m_renew_2",
        plan_id=plan_a.id,
        start_date=today - timedelta(days=50),
        end_date=today - timedelta(days=20),
        status="expired",
    )
    session.add(old_ms)
    session.commit()

    renewed = renew_or_create_membership(session, "m_renew_2", plan_a.id, gym_a.id)
    assert renewed.start_date == today
    assert renewed.end_date == today + timedelta(days=plan_a.duration_days)


def test_freeze_pushes_end_date_and_tracks_days(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    plan_a = seed_tenants["plan_a"]

    today = date.today()
    ms = Membership(
        gym_id=gym_a.id,
        member_id="m_freeze_1",
        plan_id=plan_a.id,
        start_date=today - timedelta(days=10),
        end_date=today + timedelta(days=20),
        status="active",
        frozen_days_used=0,
    )
    session.add(ms)
    session.commit()

    original_end = ms.end_date
    updated = freeze_membership(session, ms.id, freeze_days=7, reason="Travel", gym_id=gym_a.id)
    assert updated.status == "frozen"
    assert updated.frozen_days_used == 7
    assert updated.end_date == original_end + timedelta(days=7)


def test_freeze_blocks_when_exceeding_max_freeze_days(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    plan_a = seed_tenants["plan_a"]  # max_freeze_days is 14

    today = date.today()
    ms = Membership(
        gym_id=gym_a.id,
        member_id="m_freeze_2",
        plan_id=plan_a.id,
        start_date=today,
        end_date=today + timedelta(days=30),
        status="active",
        frozen_days_used=10,
    )
    session.add(ms)
    session.commit()

    # Attempting to freeze for 5 days when 10 + 5 = 15 > 14
    with pytest.raises(HTTPException) as exc:
        freeze_membership(session, ms.id, freeze_days=5, reason="Exam", gym_id=gym_a.id)
    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "MAX_FREEZE_EXCEEDED"
