import logging

from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from modules.config import get_config

logger = logging.getLogger("noattack.redis")

KEY = "under_attack"


class RedisCache:
    def __init__(self):
        cfg = get_config()
        self.redis = Redis(
            host=cfg.get("REDIS", "HOST"),
            port=cfg.get("REDIS", "PORT"),
            password=cfg.get("REDIS", "PASSWORD"),
        )
        self._ttl = cfg.get("SETTINGS", "ATTACK_COOLDOWN_TTL")

    async def check(self):
        """Check if Redis is reachable."""
        try:
            await self.redis.ping()
            return True
        except RedisConnectionError as e:
            logger.warning("Redis unreachable: %s", e)
            return False

    async def is_under_attack(self):
        """Return True if the under-attack flag is set in Redis."""
        try:
            return await self.redis.exists(KEY) > 0
        except RedisConnectionError as e:
            logger.error("Redis error: %s", e)
            return False

    async def set_under_attack(self):
        """Set the under-attack flag with the configured TTL."""
        try:
            await self.redis.set(KEY, 1, ex=self._ttl)
        except RedisConnectionError as e:
            logger.error("Redis error: %s", e)

    async def ttl(self):
        """Return the remaining TTL of the under-attack flag in seconds."""
        try:
            return await self.redis.ttl(KEY)
        except RedisConnectionError:
            return -1
