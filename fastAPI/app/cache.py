import logging
import redis.asyncio as redis
from datetime import datetime, timedelta
import json
from .schemas import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self):
        self.redis = redis.Redis.from_url(
            Config.REDIS_URL,
            decode_responses=True,
            socket_timeout=10,
            socket_connect_timeout=10,
            retry_on_timeout=True
        )

    def _get_cache_key(self, prefix: str, params: dict) -> str:
        sorted_params = sorted(params.items())
        param_str = "_".join(f"{k}={v}" for k, v in sorted_params if v is not None)
        return f"{prefix}:{param_str}" if param_str else prefix

    def _get_ttl(self):
        now = datetime.now()
        reset_time = datetime.strptime("14:11", "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )

        if now >= reset_time:
            reset_time += timedelta(days=1)

        ttl = int((reset_time - now).total_seconds())
        return max(ttl, 1)

    async def get(self, prefix: str, params: dict):
        key = self._get_cache_key(prefix, params)
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Ошибка при чтении кэша: {e}")
        return None

    async def set(self, prefix: str, params: dict, data: dict):
        key = self._get_cache_key(prefix, params)
        ttl = self._get_ttl()
        try:
            await self.redis.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            print(f"Ошибка при записи кэша: {e}")

    async def get_or_set(self, prefix: str, params: dict, data):
        cached = await self.get(prefix, params)
        if cached is not None:
            return cached

        result = data
        await self.set(prefix, params, result)
        return result


def create_cache():
    cache_service = CacheService()
    return cache_service
