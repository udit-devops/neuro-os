import redis

from app.core.config import settings

_redis: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


def enqueue_document(document_id: int) -> None:
    get_redis().lpush(settings.INGESTION_QUEUE, str(document_id))


def pop_document(timeout: int = 1) -> int | None:
    result = get_redis().brpop(settings.INGESTION_QUEUE, timeout=timeout)
    if not result:
        return None
    return int(result[1])
