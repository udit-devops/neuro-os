import logging

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_limiter() -> Limiter:
    try:
        return Limiter(
            key_func=get_remote_address,
            storage_uri=settings.REDIS_URL,
            strategy="moving-window",
        )
    except Exception as exc:
        logger.warning(
            "rate limiter falling back to in-memory storage (%s)", exc
        )
        return Limiter(
            key_func=get_remote_address,
            storage_uri="memory://",
            strategy="moving-window",
        )


limiter = _build_limiter()
