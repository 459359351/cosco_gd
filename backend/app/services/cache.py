import json
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


async def get_cache(key: str) -> Any | None:
    try:
        payload = await redis_client.get(key)
        if not payload:
            return None
        return json.loads(payload)
    except RedisError:
        return None
    except Exception:
        return None


async def set_cache(key: str, value: Any, ttl: int = 30) -> None:
    try:
        await redis_client.set(key, json.dumps(value), ex=ttl)
    except RedisError:
        pass
    except Exception:
        pass
