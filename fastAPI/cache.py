import redis.asyncio as redis
from datetime import datetime, timedelta
import json
from config import Config


class CacheService:
    def __init__(self):
        self.redis = redis.Redis.from_url(
            Config.REDIS_URL,
            decode_responses=True,
            socket_timeout=2,  # Таймаут на операцию 2 сек
            socket_connect_timeout=2,  # Таймаут на подключение 2 сек
            retry_on_timeout=True
        )
        self.reset_time = Config.CACHE_RESET_TIME

    def _get_cache_key(self, prefix: str, params: dict) -> str:
        """Формирует ключ для кэша на основе параметров"""
        sorted_params = sorted(params.items())
        param_str = "_".join(f"{k}={v}" for k, v in sorted_params if v is not None)
        return f"{prefix}:{param_str}" if param_str else prefix

    def _get_ttl(self) -> int:
        now = datetime.now()
        reset_time = datetime.strptime(self.reset_time, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )

        if now >= reset_time:
            reset_time += timedelta(days=1)

        ttl = int((reset_time - now).total_seconds())
        return max(ttl, 1)

    async def get(self, prefix: str, params: dict):
        """Получает данные из кэша"""
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

    async def clear_cache(self):
        try:
            await self.redis.flushdb()
        except Exception as e:
            print(f"Ошибка при очистке кэша: {e}")

    async def get_or_set(self, prefix: str, params: dict, func):
        """Получает из кэша или выполняет функцию и кэширует результат"""
        cached = await self.get(prefix, params)
        if cached is not None:
            return cached

        result = await func()
        await self.set(prefix, params, result)
        return result


cache_service = CacheService()
