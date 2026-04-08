import logging

import aiohttp

from modules.config import get_config

logger = logging.getLogger("noattack.cloudflare")


class Cloudflare:
    def __init__(self):
        self._cfg = get_config()
        self._session = None

    def _headers(self):
        """Build the Cloudflare API auth headers."""
        return {
            "Authorization": f"Bearer {self._cfg.get('CLOUDFLARE', 'API_KEY')}",
            "Content-Type": "application/json",
        }

    async def _get_session(self):
        """Return the shared aiohttp session, creating it if needed."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the shared HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_zone(self, zone_id):
        """Return the zone name for the given zone ID, or None on error."""
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}"
        try:
            session = await self._get_session()
            async with session.get(url, headers=self._headers()) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data["result"]["name"]
        except (aiohttp.ClientError, KeyError) as e:
            logger.error("Failed to fetch zone %s: %s", zone_id, e)
            return None

    async def get_zone_under_attack(self, zone_id):
        """Return True if the zone is in under_attack mode, False if not, None on error."""
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/security_level"
        try:
            session = await self._get_session()
            async with session.get(url, headers=self._headers()) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data["result"]["value"] == "under_attack"
        except (aiohttp.ClientError, KeyError) as e:
            logger.error("Failed to get security level for zone %s: %s", zone_id, e)
            return None

    async def set_zone_under_attack(self, zone_id, under_attack):
        """Set the security level for a zone. Returns True on success."""
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/security_level"
        payload = {"value": "under_attack" if under_attack else "essentially_off"}
        try:
            session = await self._get_session()
            async with session.patch(url, headers=self._headers(), json=payload) as resp:
                resp.raise_for_status()
                return True
        except aiohttp.ClientError as e:
            logger.error("Failed to set security level for zone %s: %s", zone_id, e)
            return False
