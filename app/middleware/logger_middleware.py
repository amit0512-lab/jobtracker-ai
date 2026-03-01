import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("jobtracker")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Request log
        logger.info(f"➡️  {request.method} {request.url.path} | IP: {request.client.host}")

        response = await call_next(request)

        # Response log
        duration = round((time.time() - start_time) * 1000, 2)
        logger.info(
            f"✅ {request.method} {request.url.path} "
            f"| Status: {response.status_code} "
            f"| Time: {duration}ms"
        )

        return response