import aiohttp

from modules import config


class Cloudflare:
    def __init__(self):
        self.config = config.Config()

    async def get_header(self) -> dict:
        """
        Get headers for Cloudflare API.
        :return: A dictionary containing the headers.
        """
        return {
            "Authorization": f"Bearer {self.config.get('CLOUDFLARE', 'API_KEY')}",
            "Content-Type": "application/json"
        }

    async def get_zone(self, zone_id: str) -> dict:
        """
        Get a zone from Cloudflare.
        :param zone_id: The ID of the zone.
        :return: A dictionary containing the zone information.
        """
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        url=url,
                        headers=await self.get_header()
                ) as response:
                    return await response.json()

        except aiohttp.ClientConnectorError as e:
            raise ConnectionError(f"Connection error: {e}") from e
        except aiohttp.ClientResponseError as e:
            raise ValueError(f"Response error: {e}") from e

    async def get_zone_under_attack(self, zone_id: str) -> dict:
        """
        Get the security level of a zone from Cloudflare.
        :param zone_id: The ID of the zone.
        :return: A dictionary containing the security level information.
        """
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/security_level"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        url=url,
                        headers=await self.get_header()
                ) as response:
                    return await response.json()

        except aiohttp.ClientConnectorError as e:
            raise ConnectionError(f"Connection error: {e}") from e

        except aiohttp.ClientResponseError as e:
            raise ValueError(f"Response error: {e}") from e

    async def set_zone_under_attack(self, zone_id: str, mode: bool) -> dict:
        """
        Set a zone under attack mode.
        :param zone_id: The ID of the zone.
        :param mode: True to enable under attack mode, False to disable.
        :return: A dictionary containing the response from Cloudflare.
        """
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/security_level"
        data = {
            "value": "under_attack" if mode else "essentially_off"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.patch(
                        url=url,
                        headers=await self.get_header(),
                        json=data
                ) as response:
                    return await response.json()

        except aiohttp.ClientConnectorError as e:
            raise ConnectionError(f"Connection error: {e}") from e

        except aiohttp.ClientResponseError as e:
            raise ValueError(f"Response error: {e}") from e
