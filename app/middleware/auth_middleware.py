from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token, is_token_blacklisted
from app.models.user import User
from uuid import UUID
from app.core.redis import get_redis as _get_redis

# Bearer token extractor
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Inject into protected routes to get the current logged-in user.
    Usage: user: User = Depends(get_current_user)
    """
    token = credentials.credentials

    # 1. Check if token is blacklisted (user logged out)
    if await is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid, please login again"
        )

    # 2. Decode the token
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # 3. Fetch the user from database
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token"
        )

    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    return user


async def rate_limit(request: Request, max_requests: int = 60, window: int = 60):
    """
    Per-IP rate limiting - 60 requests per minute by default
    Use 5 requests per minute for login route
    """
    client_ip = request.client.host
    key = f"ratelimit:{client_ip}:{request.url.path}"
    r = _get_redis()

    current = await r.incr(key)
    if current == 1:
        await r.expire(key, window)  # Set expiry on first request

    if current > max_requests:
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Please try again after {window} seconds."
        )
