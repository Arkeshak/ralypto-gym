from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.member import Member
from app.models.payment import Due, Payment
from app.models.user import User
from app.schemas.api import PaymentCreate
from app.security.dependencies import get_current_user, require_role
from app.services.membership_service import format_money
from app.services.payment_service import (
    get_daily_cash_summary,
    get_receipt_data,
    mark_due_paid,
    record_payment,
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/")
def list_payments(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    gym_id = current_user.gym_id
    query = (
        select(Payment, Member)
        .join(Member, Member.id == Payment.member_id)
        .where(Payment.gym_id == gym_id)
        .order_by(Payment.paid_at.desc())
    )
    results = session.exec(query).all()

    items = []
    for payment, member in results:
        items.append({
            "id": payment.id,
            "invoice_no": payment.invoice_no,
            "member_id": member.id,
            "member_name": member.name,
            "member_code": member.member_code,
            "amount_cents": payment.amount_cents,
            "amount_formatted": format_money(payment.amount_cents),
            "method": payment.method,
            "paid_at": payment.paid_at.isoformat(),
            "reference": payment.reference,
            "status": "Paid",
        })

    start = (page - 1) * limit
    paged = items[start : start + limit]

    return {
        "items": paged,
        "total": len(items),
        "page": page,
        "limit": limit,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_payment(
    req: PaymentCreate,
    current_user: User = Depends(require_role(["owner", "manager", "front_desk"])),
    session: Session = Depends(get_session),
):
    payment = record_payment(
        session=session,
        gym_id=current_user.gym_id,
        member_id=req.member_id,
        amount_cents=req.amount_cents,
        method=req.method,
        membership_id=req.membership_id,
        reference=req.reference,
        received_by=current_user.name,
        note=req.note,
    )
    return {
        "id": payment.id,
        "invoice_no": payment.invoice_no,
        "amount_cents": payment.amount_cents,
        "amount_formatted": format_money(payment.amount_cents),
        "method": payment.method,
        "paid_at": payment.paid_at.isoformat(),
    }


@router.get("/dues")
def list_dues(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    gym_id = current_user.gym_id
    query = (
        select(Due, Member)
        .join(Member, Member.id == Due.member_id)
        .where(Due.gym_id == gym_id, Due.status == "open")
        .order_by(Due.due_date.asc())
    )
    results = session.exec(query).all()

    items = []
    for due, member in results:
        clean_phone = member.phone.replace("+", "").replace(" ", "")
        remind_text = f"Reminder from Iron Peak Fitness: Outstanding fee of {format_money(due.amount_cents)} was due on {due.due_date.strftime('%b %d')}. Please visit front desk to settle."
        wa_url = f"https://wa.me/{clean_phone}?text={remind_text.replace(' ', '%20')}"

        items.append({
            "id": due.id,
            "member_id": member.id,
            "member_name": member.name,
            "member_code": member.member_code,
            "member_phone": member.phone,
            "amount_cents": due.amount_cents,
            "amount_formatted": format_money(due.amount_cents),
            "due_date": due.due_date.isoformat(),
            "reason": due.reason or "Membership renewal",
            "whatsapp_reminder_url": wa_url,
        })
    return items


@router.post("/dues/{id}/mark-paid")
def pay_due(
    id: str,
    method: str = "cash",
    current_user: User = Depends(require_role(["owner", "manager", "front_desk"])),
    session: Session = Depends(get_session),
):
    payment = mark_due_paid(
        session=session,
        due_id=id,
        gym_id=current_user.gym_id,
        received_by=current_user.name,
        method=method,
    )
    return {
        "status": "paid",
        "payment_id": payment.id,
        "invoice_no": payment.invoice_no,
        "amount_formatted": format_money(payment.amount_cents),
    }


@router.get("/{id}/receipt")
def get_receipt(
    id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return get_receipt_data(session=session, payment_id=id, gym_id=current_user.gym_id)


@router.get("/daily-summary")
def daily_summary(
    target_date: Optional[date] = None,
    current_user: User = Depends(require_role(["owner", "manager"])),
    session: Session = Depends(get_session),
):
    return get_daily_cash_summary(session=session, gym_id=current_user.gym_id, target_date=target_date)
