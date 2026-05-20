import asyncio
import contextlib
import json

from redis.asyncio import Redis

from app.core.config import settings
from app.ws.manager import manager

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


async def publish(channel: str, payload: dict) -> None:
    with contextlib.suppress(Exception):
        await redis_client.publish(channel, json.dumps(payload))


async def start_pubsub_bridge() -> asyncio.Task:
    pubsub = redis_client.pubsub()
    with contextlib.suppress(Exception):
        await pubsub.subscribe("cockpit.realtime")

    async def _worker() -> None:
        try:
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                data = json.loads(message["data"])
                await manager.broadcast(data)
        finally:
            with contextlib.suppress(Exception):
                await pubsub.unsubscribe("cockpit.realtime")

    return asyncio.create_task(_worker())
