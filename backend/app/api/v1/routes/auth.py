from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from app.core.config import settings
from app.db.session import get_session
from app.models.gym import Gym
from app.models.member import Member
from app.models.user import User
from app.schemas.api import (
    AuthMeResponse,
    LoginRequest,
    MemberLoginRequest,
    PinLoginRequest,
    RefreshRequest,
    TokenResponse,
)
from app.security.dependencies import get_current_user
from app.security.jwt import create_access_token, create_refresh_token, decode_token
from app.security.passwords import verify_password, verify_pin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == req.email)).first()
    if not user or not user.password_hash or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Incorrect email or password"},
        )
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "USER_INACTIVE", "message": "Account is inactive"},
        )

    access_token = create_access_token({"sub": user.id, "gym_id": user.gym_id, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.id, "gym_id": user.gym_id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        name=user.name,
        role=user.role,
        gym_id=user.gym_id,
    )


@router.post("/pin-login", response_model=TokenResponse)
def pin_login(req: PinLoginRequest, session: Session = Depends(get_session)):
    gym = session.exec(select(Gym).where(Gym.code == req.gym_code)).first()
    if not gym:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "GYM_NOT_FOUND", "message": "Gym code not found"},
        )

    # Find staff with this PIN
    users = session.exec(select(User).where(User.gym_id == gym.id, User.active == True)).all()
    matched_user = None
    for u in users:
        if u.pin_hash and verify_pin(req.pin, u.pin_hash):
            matched_user = u
            break

    if not matched_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_PIN", "message": "Invalid PIN for this gym"},
        )

    access_token = create_access_token({"sub": matched_user.id, "gym_id": matched_user.gym_id, "role": matched_user.role})
    refresh_token = create_refresh_token({"sub": matched_user.id, "gym_id": matched_user.gym_id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=matched_user.id,
        name=matched_user.name,
        role=matched_user.role,
        gym_id=matched_user.gym_id,
    )


@router.post("/member-login", response_model=TokenResponse)
def member_login(req: MemberLoginRequest, session: Session = Depends(get_session)):
    clean_phone = req.phone.strip()
    # In dev the code is always 123456
    if req.code != "123456":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CODE", "message": "Invalid login code. Dev code is 123456."},
        )

    # Find member by phone
    member = session.exec(select(Member).where(Member.phone == clean_phone, Member.deleted == False)).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "MEMBER_NOT_FOUND", "message": "Member not found with this phone number"},
        )

    # Find or create linked User
    user = session.exec(select(User).where(User.linked_member_id == member.id)).first()
    if not user:
        user = User(
            gym_id=member.gym_id,
            name=member.name,
            phone=member.phone,
            email=member.email,
            role="member",
            active=True,
            linked_member_id=member.id,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    access_token = create_access_token({"sub": user.id, "gym_id": user.gym_id, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.id, "gym_id": user.gym_id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        name=user.name,
        role=user.role,
        gym_id=user.gym_id,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(req: RefreshRequest, session: Session = Depends(get_session)):
    try:
        payload = decode_token(req.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid refresh token: {str(e)}")

    user = session.get(User, user_id)
    if not user or not user.active:
        raise HTTPException(status_code=401, detail="User inactive or not found")

    access_token = create_access_token({"sub": user.id, "gym_id": user.gym_id, "role": user.role})
    new_refresh = create_refresh_token({"sub": user.id, "gym_id": user.gym_id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh,
        user_id=user.id,
        name=user.name,
        role=user.role,
        gym_id=user.gym_id,
    )


@router.get("/me", response_model=AuthMeResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    gym = session.get(Gym, current_user.gym_id)
    gym_name = gym.name if gym else "Ralypto Gym"
    plan = gym.plan if gym else "Premium"
    plan_status = gym.plan_status if gym else "active"

    features = list(settings.PLAN_FEATURES.get(plan, set()))
    limit = settings.PLAN_MEMBER_LIMITS.get(plan, 150)
    current_count = session.exec(
        select(func.count(Member.id)).where(Member.gym_id == current_user.gym_id, Member.deleted == False)
    ).one()

    return AuthMeResponse(
        user_id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        role=current_user.role,
        language=current_user.language,
        gym_id=current_user.gym_id,
        gym_name=gym_name,
        plan=plan,
        plan_status=plan_status,
        features=features,
        member_limit=limit,
        current_member_count=current_count,
        linked_member_id=current_user.linked_member_id,
    )
