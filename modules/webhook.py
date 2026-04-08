import logging
from datetime import datetime, timezone

import aiohttp

from modules.config import get_config

logger = logging.getLogger("noattack.webhook")


class Webhook:
    def __init__(self):
        self._cfg = get_config()

    async def send(self, action, zone, color=0x00FF00):
        """Send a Discord embed notification for a zone action."""
        url = self._cfg.get("SETTINGS", "WEBHOOK")
        if not url:
            return

        payload = {
            "username": "NoAttack",
            "embeds": [{
                "title": action,
                "description": f"Zone: **{zone}**",
                "color": color,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }],
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    resp.raise_for_status()
        except aiohttp.ClientError as e:
            logger.error("Discord webhook failed: %s", e)
