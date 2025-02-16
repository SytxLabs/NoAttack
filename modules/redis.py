from enum import Enum

from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from modules import config


class CacheType(Enum):
    UNDER_ATTACK = "under_attack"

class RedisCache:

    def __init__(self):
        self.config = config.Config()
        self.redis = Redis(
            host=self.config.get("REDIS", "HOST"),
            port=self.config.get("REDIS", "PORT"),
            password=self.config.get("REDIS", "PASSWORD")
        )

    async def get(self, key: str | None, cache_type: CacheType) -> str | bool | None:
        """
        Get a value from the cache file.
        :param key: The key to retrieve (or None).
        :param cache_type: The type of cache (Enum).
        :return: The decoded string if present, None if missing, or False on connection error.
        """
        if not await self.check():
            return False

        query = f"{cache_type.value}" if key is None else f"{key}:{cache_type.value}"
        data = await self.redis.get(query)
        return data.decode('utf-8') if data else None

    async def set(self, key: str | None, value: str, cache_type: CacheType, ttl: int = 300) -> bool:
        """
        Set a value in the cache with an optional TTL.
        :param key: The key to set (or None).
        :param value: The value to store.
        :param cache_type: The type of cache (Enum).
        :param ttl: Time-to-live in seconds.
        :return: True if successful, False on connection error.
        """
        if not await self.check():
            return False

        query = f"{cache_type.value}" if key is None else f"{key}:{cache_type.value}"
        return await self.redis.set(query, value, ex=ttl)

    async def exists(self, key: str | None, cache_type: CacheType) -> bool:
        """
        Check if a key exists in the cache.
        :param key: The key to check (or None).
        :param cache_type: The type of cache (Enum).
        :return: True if key exists, False otherwise or on connection error.
        """
        if not await self.check():
            return False

        query = f"{cache_type.value}" if key is None else f"{key}:{cache_type.value}"
        return await self.redis.exists(query) > 0

    async def delete(self, key: str | None, cache_type: CacheType) -> int | bool:
        """
        Delete a key from the cache.
        :param key: The key to delete (or None).
        :param cache_type: The type of cache (Enum).
        :return: The number of deleted keys or False on connection error.
        """
        if not await self.check():
            return False

        query = f"{cache_type.value}" if key is None else f"{key}:{cache_type.value}"
        return await self.redis.delete(query)

    async def check(self) -> bool:
        """
        Check if the cache is connected.
        :return: True if connected, False otherwise.
        """
        try:
            await self.redis.ping()
            return True
        except RedisConnectionError:
            return False

    async def flush(self) -> bool:
        """
        Flush the entire cache.
        :return: True if successful, False otherwise.
        """
        if not await self.check():
            return False

        keys = await self.redis.keys()
        for k in keys:
            await self.redis.delete(k)
        return True

    async def set_under_attack(self):
        """
        Set the 'Under Attack' status in Redis for 5 minutes.
        """
        await self.set("under_attack", "True", CacheType.UNDER_ATTACK, ttl=300)

    async def clear_under_attack(self):
        """
        Clear the 'Under Attack' status in Redis.
        """
        await self.delete("under_attack", CacheType.UNDER_ATTACK)

    async def is_under_attack(self) -> bool:
        """
        Check if the site is under attack.
        :return: True, if under attack, False otherwise.
        """
        value = await self.get("under_attack", CacheType.UNDER_ATTACK)
        return value == "True"
