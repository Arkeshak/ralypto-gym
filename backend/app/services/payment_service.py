from datetime import date, datetime, timezone
from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from sqlmodel import Session, select, func
from app.models.base import utc_now
from app.models.gym import Gym, GymSettings
from app.models.member import Member
from app.models.payment import Due, Payment
from app.services.membership_service import format_money


def generate_invoice_no(session: Session, gym_id: str) -> str:
    count = session.exec(
        select(func.count(Payment.id)).where(Payment.gym_id == gym_id)
    ).one()
    return f"INV-{(count + 1):04d}"


def record_payment(
    session: Session,
    gym_id: str,
    member_id: str,
    amount_cents: int,
    method: str = "cash",
    membership_id: Optional[str] = None,
    reference: Optional[str] = None,
    received_by: Optional[str] = None,
    note: Optional[str] = None,
) -> Payment:
    member = session.get(Member, member_id)
    if not member or member.gym_id != gym_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "MEMBER_NOT_FOUND", "message": "Member not found"},
        )

    invoice_no = generate_invoice_no(session, gym_id)
    payment = Payment(
        gym_id=gym_id,
        member_id=member_id,
        membership_id=membership_id,
        amount_cents=amount_cents,
        method=method,
        reference=reference,
        invoice_no=invoice_no,
        received_by=received_by,
        paid_at=utc_now(),
        note=note,
    )
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment


def mark_due_paid(
    session: Session,
    due_id: str,
    gym_id: str,
    received_by: Optional[str] = None,
    method: str = "cash",
) -> Payment:
    due = session.get(Due, due_id)
    if not due or due.gym_id != gym_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DUE_NOT_FOUND", "message": "Due entry not found"},
        )
    if due.status == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "ALREADY_PAID", "message": "This due is already paid"},
        )

    due.status = "paid"
    due.updated_at = utc_now()
    session.add(due)

    payment = record_payment(
        session=session,
        gym_id=gym_id,
        member_id=due.member_id,
        amount_cents=due.amount_cents,
        method=method,
        reference=f"Due #{due.id[:8]}",
        received_by=received_by,
        note=f"Settled due: {due.reason or 'Membership fee'}",
    )
    return payment


def get_receipt_data(session: Session, payment_id: str, gym_id: str) -> Dict[str, Any]:
    payment = session.get(Payment, payment_id)
    if not payment or payment.gym_id != gym_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PAYMENT_NOT_FOUND", "message": "Payment not found"},
        )

    gym = session.get(Gym, gym_id)
    member = session.get(Member, payment.member_id)
    settings = session.exec(
        select(GymSettings).where(GymSettings.gym_id == gym_id)
    ).first()

    header = settings.receipt_header if settings else (gym.name if gym else "Gym Receipt")
    footer = settings.receipt_footer if settings else "Thank you for training with us!"

    clean_phone = member.phone.replace("+", "").replace(" ", "") if member and member.phone else ""
    wa_text = f"Receipt {payment.invoice_no}: Received {format_money(payment.amount_cents)} on {payment.paid_at.strftime('%Y-%m-%d')} for {gym.name if gym else 'Gym'}. Thank you!"
    wa_url = f"https://wa.me/{clean_phone}?text={wa_text.replace(' ', '%20')}" if clean_phone else None

    return {
        "invoice_no": payment.invoice_no,
        "payment_id": payment.id,
        "member_name": member.name if member else "Member",
        "member_code": member.member_code if member else "",
        "member_phone": member.phone if member else "",
        "amount_cents": payment.amount_cents,
        "amount_formatted": format_money(payment.amount_cents),
        "method": payment.method,
        "paid_at": payment.paid_at.isoformat(),
        "reference": payment.reference,
        "received_by": payment.received_by or "Front desk",
        "gym_name": gym.name if gym else "Gym",
        "receipt_header": header,
        "receipt_footer": footer,
        "whatsapp_url": wa_url,
    }


def get_daily_cash_summary(session: Session, gym_id: str, target_date: Optional[date] = None) -> Dict[str, Any]:
    query_date = target_date or date.today()
    start_dt = datetime.combine(query_date, datetime.min.time(), tzinfo=timezone.utc)
    end_dt = datetime.combine(query_date, datetime.max.time(), tzinfo=timezone.utc)

    payments = session.exec(
        select(Payment).where(
            Payment.gym_id == gym_id,
            Payment.paid_at >= start_dt,
            Payment.paid_at <= end_dt,
        )
    ).all()

    methods_breakdown = {"cash": 0, "card": 0, "bank": 0, "online": 0}
    total_cents = 0

    for p in payments:
        total_cents += p.amount_cents
        m = p.method.lower()
        if m in methods_breakdown:
            methods_breakdown[m] += p.amount_cents
        else:
            methods_breakdown["cash"] += p.amount_cents

    return {
        "date": query_date.isoformat(),
        "total_cents": total_cents,
        "total_formatted": format_money(total_cents),
        "count": len(payments),
        "methods": {
            k: {"cents": v, "formatted": format_money(v)}
            for k, v in methods_breakdown.items()
        },
    }
