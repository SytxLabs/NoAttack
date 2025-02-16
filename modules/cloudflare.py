import aiohttp

from modules import config


class Cloudflare:
    def __init__(self):
        self.config = config.Config()

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

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        url=url,
                        headers=await self.getHeaders()
                ) as response:
                    return await response.json()
        except aiohttp.client.ClientConnectorDNSError:
            raise Exception("Failed to connect to Cloudflare API")
            return False

    async def getZoneUnderAttack(self, zone_id: str) -> dict:
        """
        Get a zone from Cloudflare
        :param zone_id:
        :return:
        """
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/security_level"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        url=url,
                        headers=await self.getHeaders()
                ) as response:
                    return await response.json()
        except aiohttp.client.ClientConnectorDNSError:
            raise Exception("Failed to connect to Cloudflare API")
            return False

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

        try:
            async with aiohttp.ClientSession() as session:
                async with session.patch(
                        url=url,
                        headers=await self.getHeaders(),
                        json=data
                ) as response:
                    return await response.json()
        except aiohttp.client.ClientConnectorDNSError:
            raise Exception("Failed to connect to Cloudflare API")
            return False
