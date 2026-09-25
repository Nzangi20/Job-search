from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import (
    PasswordResetConfirm,
    PasswordResetRequest,
    Token,
    UserLogin,
    UserOut,
    UserRegister,
)
from app.services.auth import (
    create_access_token,
    create_user,
    generate_reset_token,
    get_user_by_email,
    verify_password,
)
from app.api.deps import get_current_user
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await create_user(db, payload.email, payload.password, payload.full_name)
    token = create_access_token(user.id)
    return Token(access_token=token)


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        search_interval_hours=user.search_interval_hours,
    )


@router.post("/password-reset/request")
async def password_reset_request(payload: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, payload.email)
    if user:
        user.reset_token = generate_reset_token()
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/password-reset/confirm")
async def password_reset_confirm(payload: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select

    from app.services.auth import hash_password

    result = await db.execute(select(User).where(User.reset_token == payload.token))
    user = result.scalar_one_or_none()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user.hashed_password = hash_password(payload.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    return {"message": "Password updated"}
