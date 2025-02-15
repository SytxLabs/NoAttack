import aiohttp

from driver import Config


class Cloudflare:
    def __init__(self):
        self.config = Config.Config()

    async def getHeaders(self) -> dict:
        """
        Get headers for Cloudflare API
        :return:
        """
        return {
            "Authorization": f"Bearer {self.config.get('CLOUDFLARE', 'API_KEY')}",
            "Content-Type": "application/json"
        }

    async def getZone(self, zone_id: str) -> dict:
        """
        Get a zone from Cloudflare
        :param zone_id:
        :return:
        """
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=await self.getHeaders()) as response:
                return await response.json()

    async def getZoneUnderAttack(self, zone_id: str) -> dict:
        """
        Get a zone from Cloudflare
        :param zone_id:
        :return:
        """
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/security_level"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=await self.getHeaders()) as response:
                return await response.json()

    async def setZoneUnderAttack(self, zone_id: str, mode: bool) -> dict:
        """
        Set a zone under attack mode
        :param zone_id:
        :param mode:
        :return:
        """
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/security_level"
        data = {
            "value": "under_attack" if mode else "essentially_off"
        }

        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=await self.getHeaders(), json=data) as response:
                return await response.json()
