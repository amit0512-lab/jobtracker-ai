import redis.asyncio as aioredis
from app.core.config import settings

# Connection pool banao — har request pe naya connection nahi banega
redis_pool = aioredis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=20,
    decode_responses=True  # bytes ki jagah string milega
)


def get_redis() -> aioredis.Redis:
    """FastAPI dependency — routes mein inject hoga"""
    return aioredis.Redis(connection_pool=redis_pool)


async def set_key(key: str, value: str, expire_seconds: int = None):
    """Key set karo with optional expiry"""
    r = get_redis()
    await r.set(key, value, ex=expire_seconds)


async def get_key(key: str) -> str | None:
    """Key ki value fetch karo"""
    r = get_redis()
    return await r.get(key)


async def delete_key(key: str):
    """Key delete karo (logout ke waqt token blacklist)"""
    r = get_redis()
    await r.delete(key)


async def key_exists(key: str) -> bool:
    """Check karo key exist karti hai ya nahi"""
    r = get_redis()
    return await r.exists(key) > 0