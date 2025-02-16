import aiohttp

from modules import config


class Webhook:
    def __init__(self):
        self.config = config.Config()

    async def send(self, message: str, color: int = 0x00FF00):
        """
        Send a message to a Discord webhook.
        :param message: The message to send.
        :param color: The color of the message embed.
        """
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
            async with session.post(
                    url=webhook_url,
                    json=data
            ) as resp:
                resp.raise_for_status()

    def get_webhook_url(self) -> str:
        """
        Get the webhook URL from the config.
        :return:
        """
        return self.config.get("SETTINGS", "WEBHOOK")
