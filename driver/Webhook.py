import aiohttp

from driver import Config


class Webhook:
    def __init__(self):
        self.config = Config.Config()

    async def send(self, message: str, color: int = 0x00FF00):
        data = {
            'username': 'NoAttack',
            'embeds': [
                {
                    'title': 'NoAttack',
                    'description': message,
                    'color': color,
                }
            ]
        }

        webhook_url = self.config.get("SETTINGS", "WEBHOOK")
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=data) as resp:
                resp.raise_for_status()
