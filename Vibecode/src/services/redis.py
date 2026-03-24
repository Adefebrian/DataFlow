import redis.asyncio as aioredis
import json
from typing import Callable, AsyncGenerator
from src.config import get_settings
import logging

logger = logging.getLogger(__name__)


class RedisService:
    def __init__(self):
        self.settings = get_settings()
        self.client: aioredis.Redis | None = None
        self._connected = False

    async def connect(self):
        try:
            self.client = aioredis.from_url(
                self.settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=False,
                socket_connect_timeout=5,
            )
            self._connected = True
            logger.info("Redis client initialized")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Running without Redis.")
            self.client = None
            self._connected = False

    async def disconnect(self):
        if self.client:
            await self.client.close()

    async def publish(self, channel: str, message: dict):
        if self.client:
            try:
                await self.client.publish(channel, json.dumps(message))
            except Exception as e:
                logger.warning(f"Redis publish failed: {e}")

    async def subscribe(self, channel: str) -> aioredis.client.PubSub | None:
        if self.client:
            pubsub = self.client.pubsub()
            await pubsub.subscribe(channel)
            return pubsub
        return None

    async def stream_updates(self, job_id: str) -> AsyncGenerator[dict, None]:
        channel = f"pipeline_updates:{job_id}"
        pubsub = await self.subscribe(channel)
        if not pubsub:
            return

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield json.loads(message["data"].decode())
                else:
                    yield {"type": "HEARTBEAT"}
        finally:
            await pubsub.unsubscribe(channel)

    async def setex(self, key: str, ttl: int, value: str):
        if self.client:
            try:
                await self.client.setex(key, ttl, value)
            except Exception as e:
                logger.warning(f"Redis setex failed: {e}")

    async def get(self, key: str) -> bytes | None:
        if self.client:
            try:
                return await self.client.get(key)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
        return None


redis_service = RedisService()


async def get_redis() -> RedisService:
    return redis_service
