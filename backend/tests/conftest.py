import pytest
from datetime import date, datetime, timedelta, timezone
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine
from fastapi.testclient import TestClient
from app.core.config import settings
from app.db.session import get_session
from app.main import app
from app.models.base import utc_now
from app.models.gym import Gym, GymSettings
from app.models.member import Member
from app.models.plan import MembershipPlan, Membership
from app.models.user import User
from app.security.jwt import create_access_token
from app.security.passwords import hash_password, hash_pin

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(name="seed_tenants")
def seed_tenants_fixture(session: Session):
    # Gym A: Premium
    gym_a = Gym(
        name="Iron Peak Fitness",
        code="IPF",
        plan="Premium",
        plan_status="active",
    )
    session.add(gym_a)

    # Gym B: Basic
    gym_b = Gym(
        name="City Fit Club",
        code="CFC",
        plan="Basic",
        plan_status="active",
    )
    session.add(gym_b)
    session.commit()
    session.refresh(gym_a)
    session.refresh(gym_b)

    # Settings
    settings_a = GymSettings(gym_id=gym_a.id, grace_days=7)
    settings_b = GymSettings(gym_id=gym_b.id, grace_days=5)
    session.add(settings_a)
    session.add(settings_b)

    # Plans
    plan_a = MembershipPlan(gym_id=gym_a.id, name="Monthly", duration_days=30, price_cents=500000, max_freeze_days=14)
    plan_b = MembershipPlan(gym_id=gym_b.id, name="Basic Monthly", duration_days=30, price_cents=300000, max_freeze_days=7)
    session.add(plan_a)
    session.add(plan_b)

    # Users
    pwd = hash_password("Pass1234!")
    pin = hash_pin("1234")

    owner_a = User(gym_id=gym_a.id, name="Owner A", email="owner@a.com", role="owner", password_hash=pwd)
    manager_a = User(gym_id=gym_a.id, name="Manager A", email="mgr@a.com", role="manager", password_hash=pwd)
    frontdesk_a = User(gym_id=gym_a.id, name="Frontdesk A", email="fd@a.com", role="front_desk", password_hash=pwd, pin_hash=pin)
    trainer_a = User(gym_id=gym_a.id, name="Trainer A", email="tr@a.com", role="trainer", password_hash=pwd)

    owner_b = User(gym_id=gym_b.id, name="Owner B", email="owner@b.com", role="owner", password_hash=pwd)

    session.add_all([owner_a, manager_a, frontdesk_a, trainer_a, owner_b])
    session.commit()

    return {
        "gym_a": gym_a,
        "gym_b": gym_b,
        "plan_a": plan_a,
        "plan_b": plan_b,
        "owner_a": owner_a,
        "manager_a": manager_a,
        "frontdesk_a": frontdesk_a,
        "trainer_a": trainer_a,
        "owner_b": owner_b,
    }
