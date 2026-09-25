import secrets
from datetime import datetime, timedelta

from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import CandidateProfile, NotificationSettings, User, UserRole

import bcrypt

settings = get_settings()

def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except Exception:
        return False


def create_access_token(user_id: int) -> str:
    s = get_settings()
    expire = datetime.utcnow() + timedelta(minutes=s.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, s.secret_key, algorithm=s.algorithm)


def decode_token(token: str) -> int | None:
    s = get_settings()
    try:
        payload = jwt.decode(token, s.secret_key, algorithms=[s.algorithm])
        sub = payload.get("sub")
        return int(sub) if sub else None
    except JWTError:
        return None


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession, email: str, password: str, full_name: str | None = None
) -> User:
    user = User(
        email=email.lower(),
        hashed_password=hash_password(password),
        full_name=full_name,
        role=UserRole.USER,
    )
    db.add(user)
    await db.flush()
    db.add(CandidateProfile(user_id=user.id, preferred_roles=[], preferred_locations=[]))
    db.add(NotificationSettings(user_id=user.id))
    await db.flush()
    return user


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)
