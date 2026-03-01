from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.core.config import settings
from app.core import redis as redis_service


# ─── Password Utils ────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    # Bcrypt has 72 byte limit
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    # Bcrypt has 72 byte limit
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ─── Token Creation ────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ─── Token Verification ────────────────────────────────────────

def decode_token(token: str) -> Optional[dict]:
    """Token decode karo — invalid/expired hone pe None return hoga"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


# ─── Token Blacklisting (Logout ke liye) ──────────────────────

async def blacklist_token(token: str, expire_seconds: int):
    """Logout pe token ko Redis mein blacklist karo"""
    await redis_service.set_key(
        f"blacklist:{token}",
        "true",
        expire_seconds=expire_seconds
    )


async def is_token_blacklisted(token: str) -> bool:
    """Check karo token blacklist mein hai ya nahi"""
    return await redis_service.key_exists(f"blacklist:{token}")