from enum import Enum

from config import Config
from redis import Redis as aioredis


class CacheType(Enum):
    pass


class Redis(object):
    def __init__(self):
        self.redis = aioredis.Redis(
            host=Config.get("REDIS", "HOST"),
            port=Config.get("REDIS", "PORT"),
            password=Config.get("REDIS", "PASSWORD")
        )

    async def get(self, key: None, cacheType: CacheType) -> str | bool:
        """
        Get a value from the cache file.
        :param cacheType:
        :param key:
        :return:
        """
        if not await self.check():
            return False

        query = f"{key}:{cacheType.value}"
        if key is None:
            query = f"{cacheType.value}"

        data = await self.redis.get(f"{query}")
        return data.decode('utf-8') if data else None

    async def set(self, key: None, value, cacheType: CacheType) -> bool:
        """
        Set a value in the cache file.
        :param cacheType:
        :param key:
        :param value:
        :return:
        """
        if not await self.check():
            return False

        query = f"{key}:{cacheType.value}"
        if key is None:
            query = f"{cacheType.value}"

        data = await self.redis.set(query, value)

        return data

    async def exists(self, key: None, cacheType: CacheType) -> bool:
        """
        Check if a key exists in the cache file.
        :param cacheType:
        :param key:
        :return:
        """
        if not await self.check():
            return False

        query = f"{key}:{cacheType.value}"
        if key is None:
            query = f"{cacheType.value}"

        return await self.redis.exists(query)

    async def delete(self, key: None, cacheType: CacheType) -> int | bool:
        """
        Delete a key from the cache file.
        :param cacheType:
        :param key:
        :return:
        """
        if not await self.check():
            return False

        query = f"{key}:{cacheType.value}"
        if key is None:
            query = f"{cacheType.value}"

        return await self.redis.delete(query)

    async def check(self) -> bool:
        """
        Check if the cache is connected.
        :return:
        """
        try:
            await self.redis.ping()
            return True
        except aioredis.ConnectionError:
            return False

    async def flush(self) -> bool:
        """
        Flush the cache.
        :return:
        """
        if not await self.check():
            return False

        for key in await self.redis.keys():
            if key.decode('utf-8') not in self.blacklist:
                await self.redis.delete(key.decode('utf-8'))
