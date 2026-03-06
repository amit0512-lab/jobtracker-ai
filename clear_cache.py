"""Clear Redis cache for fresh analysis"""
import asyncio
from app.core.redis import get_redis

async def clear_all_cache():
    r = get_redis()
    
    # Clear all analysis cache
    analysis_keys = await r.keys("analysis:*")
    if analysis_keys:
        await r.delete(*analysis_keys)
        print(f"✅ Cleared {len(analysis_keys)} analysis cache entries")
    
    # Clear dashboard cache
    dashboard_keys = await r.keys("dashboard:*")
    if dashboard_keys:
        await r.delete(*dashboard_keys)
        print(f"✅ Cleared {len(dashboard_keys)} dashboard cache entries")
    
    # Clear jobs cache
    jobs_keys = await r.keys("jobs:*")
    if jobs_keys:
        await r.delete(*jobs_keys)
        print(f"✅ Cleared {len(jobs_keys)} jobs cache entries")
    
    print("✅ All caches cleared! Restart the backend and try analyzing again.")

if __name__ == "__main__":
    asyncio.run(clear_all_cache())
