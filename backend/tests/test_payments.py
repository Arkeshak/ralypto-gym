from datetime import date, datetime, timedelta, timezone
import pytest
from fastapi import HTTPException
from sqlmodel import Session
from app.models.member import Member
from app.models.payment import Due, Payment
from app.services.payment_service import (
    get_daily_cash_summary,
    get_receipt_data,
    mark_due_paid,
    record_payment,
)


def test_record_payment_generates_sequential_invoice_no(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    m = Member(gym_id=gym_a.id, member_code="IPF-2001", name="Payment Tester", phone="+94 77 123 4567")
    session.add(m)
    session.commit()

    p1 = record_payment(session, gym_a.id, m.id, amount_cents=500000, method="cash")
    p2 = record_payment(session, gym_a.id, m.id, amount_cents=1350000, method="card")

    assert p1.invoice_no == "INV-0001"
    assert p2.invoice_no == "INV-0002"
    assert p1.amount_cents == 500000
    assert p2.method == "card"


def test_payment_per_gym_invoice_isolation(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    gym_b = seed_tenants["gym_b"]

    ma = Member(gym_id=gym_a.id, member_code="IPF-2002", name="Member A", phone="+94 77 000 0001")
    mb = Member(gym_id=gym_b.id, member_code="CFC-2002", name="Member B", phone="+94 77 000 0002")
    session.add_all([ma, mb])
    session.commit()

    pa = record_payment(session, gym_a.id, ma.id, amount_cents=500000)
    pb = record_payment(session, gym_b.id, mb.id, amount_cents=300000)

    # Both gyms should start their own sequence at INV-0001
    assert pa.invoice_no == "INV-0001"
    assert pb.invoice_no == "INV-0001"


def test_mark_due_paid_updates_status_and_records_payment(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    m = Member(gym_id=gym_a.id, member_code="IPF-2003", name="Due Tester", phone="+94 77 999 8888")
    session.add(m)
    session.commit()

    due = Due(
        gym_id=gym_a.id,
        member_id=m.id,
        amount_cents=400000,
        due_date=date.today() - timedelta(days=5),
        status="open",
        reason="Monthly fee",
    )
    session.add(due)
    session.commit()

    pmt = mark_due_paid(session, due.id, gym_a.id, received_by="Frontdesk", method="card")
    session.refresh(due)

    assert due.status == "paid"
    assert pmt.amount_cents == 400000
    assert pmt.method == "card"


def test_mark_due_paid_blocks_already_paid(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    m = Member(gym_id=gym_a.id, member_code="IPF-2004", name="Due Tester 2", phone="+94 77 999 7777")
    session.add(m)
    session.commit()

    due = Due(
        gym_id=gym_a.id,
        member_id=m.id,
        amount_cents=400000,
        due_date=date.today(),
        status="paid",
    )
    session.add(due)
    session.commit()

    with pytest.raises(HTTPException) as exc:
        mark_due_paid(session, due.id, gym_a.id)
    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "ALREADY_PAID"


def test_receipt_data_contains_80mm_and_whatsapp_link(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    m = Member(gym_id=gym_a.id, member_code="IPF-2005", name="Receipt Tester", phone="+94 71 234 5678")
    session.add(m)
    session.commit()

    pmt = record_payment(session, gym_a.id, m.id, amount_cents=500000, method="cash")
    receipt = get_receipt_data(session, pmt.id, gym_a.id)

    assert receipt["invoice_no"] == pmt.invoice_no
    assert receipt["member_name"] == "Receipt Tester"
    assert receipt["amount_formatted"] == "Rs 5,000"
    assert "https://wa.me/94712345678" in receipt["whatsapp_url"]


def test_daily_cash_summary_calculation(session: Session, seed_tenants):
    gym_a = seed_tenants["gym_a"]
    m = Member(gym_id=gym_a.id, member_code="IPF-2006", name="Summary Tester", phone="+94 71 000 1111")
    session.add(m)
    session.commit()

    record_payment(session, gym_a.id, m.id, amount_cents=500000, method="cash")
    record_payment(session, gym_a.id, m.id, amount_cents=1350000, method="card")

    summary = get_daily_cash_summary(session, gym_a.id, target_date=date.today())
    assert summary["count"] == 2
    assert summary["total_cents"] == 1850000
    assert summary["methods"]["cash"]["cents"] == 500000
    assert summary["methods"]["card"]["cents"] == 1350000
