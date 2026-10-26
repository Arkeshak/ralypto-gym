import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.class_model import Class
from app.models.crm import Lead
from app.models.member import Member
from app.models.payment import Due, Payment
from app.security.jwt import create_access_token


def test_tenant_cannot_see_other_gym_members(client: TestClient, session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    gym_b = seed_tenants["gym_b"]
    owner_a = seed_tenants["owner_a"]
    owner_b = seed_tenants["owner_b"]

    ma = Member(gym_id=gym_a.id, member_code="IPF-A", name="Gym A Member", phone="+94 77 111 0000")
    mb = Member(gym_id=gym_b.id, member_code="CFC-B", name="Gym B Member", phone="+94 77 222 0000")
    session.add_all([ma, mb])
    session.commit()

    token_a = create_access_token({"sub": owner_a.id, "gym_id": gym_a.id, "role": owner_a.role})
    res_a = client.get("/api/v1/members/", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a.status_code == 200
    items_a = res_a.json()["items"]
    ids_a = [item["id"] for item in items_a]
    assert ma.id in ids_a
    assert mb.id not in ids_a

    token_b = create_access_token({"sub": owner_b.id, "gym_id": gym_b.id, "role": owner_b.role})
    res_b = client.get("/api/v1/members/", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.status_code == 200
    items_b = res_b.json()["items"]
    ids_b = [item["id"] for item in items_b]
    assert mb.id in ids_b
    assert ma.id not in ids_b


def test_tenant_cannot_access_other_gym_member_profile(client: TestClient, session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    gym_b = seed_tenants["gym_b"]
    owner_a = seed_tenants["owner_a"]

    mb = Member(gym_id=gym_b.id, member_code="CFC-B2", name="Gym B Secret Member", phone="+94 77 333 0000")
    session.add(mb)
    session.commit()

    token_a = create_access_token({"sub": owner_a.id, "gym_id": gym_a.id, "role": owner_a.role})
    res = client.get(f"/api/v1/members/{mb.id}", headers={"Authorization": f"Bearer {token_a}"})
    assert res.status_code == 404


def test_tenant_cannot_see_other_gym_payments(client: TestClient, session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    gym_b = seed_tenants["gym_b"]
    owner_a = seed_tenants["owner_a"]
    owner_b = seed_tenants["owner_b"]

    ma = Member(gym_id=gym_a.id, member_code="IPF-PA", name="A Member", phone="+94 77 444 0000")
    mb = Member(gym_id=gym_b.id, member_code="CFC-PB", name="B Member", phone="+94 77 555 0000")
    session.add_all([ma, mb])
    session.commit()

    pa = Payment(gym_id=gym_a.id, member_id=ma.id, amount_cents=500000, invoice_no="INV-A1")
    pb = Payment(gym_id=gym_b.id, member_id=mb.id, amount_cents=300000, invoice_no="INV-B1")
    session.add_all([pa, pb])
    session.commit()

    token_a = create_access_token({"sub": owner_a.id, "gym_id": gym_a.id, "role": owner_a.role})
    res = client.get("/api/v1/payments/", headers={"Authorization": f"Bearer {token_a}"})
    assert res.status_code == 200
    ids = [p["id"] for p in res.json()["items"]]
    assert pa.id in ids
    assert pb.id not in ids


def test_tenant_cannot_see_other_gym_dues(client: TestClient, session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    gym_b = seed_tenants["gym_b"]
    owner_a = seed_tenants["owner_a"]

    from datetime import date
    mb = Member(gym_id=gym_b.id, member_code="CFC-DB", name="B Due Member", phone="+94 77 666 0000")
    session.add(mb)
    session.commit()

    db = Due(gym_id=gym_b.id, member_id=mb.id, amount_cents=250000, due_date=date.today(), status="open")
    session.add(db)
    session.commit()

    token_a = create_access_token({"sub": owner_a.id, "gym_id": gym_a.id, "role": owner_a.role})
    res = client.get("/api/v1/payments/dues", headers={"Authorization": f"Bearer {token_a}"})
    assert res.status_code == 200
    ids = [d["id"] for d in res.json()]
    assert db.id not in ids


def test_tenant_cannot_see_other_gym_leads(client: TestClient, session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    gym_b = seed_tenants["gym_b"]
    owner_a = seed_tenants["owner_a"]

    lead_b = Lead(gym_id=gym_b.id, name="Lead at CFC", phone="+94 77 777 0000", status="new")
    session.add(lead_b)
    session.commit()

    token_a = create_access_token({"sub": owner_a.id, "gym_id": gym_a.id, "role": owner_a.role})
    res = client.get("/api/v1/crm/leads", headers={"Authorization": f"Bearer {token_a}"})
    assert res.status_code == 200
    ids = [l["id"] for l in res.json()]
    assert lead_b.id not in ids
