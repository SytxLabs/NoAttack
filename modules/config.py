import yaml


class ConfigNotFoundError(Exception):
    pass


_DEFAULT = {
    "SETTINGS": {
        "MAX_INCOMING_TRAFFIC_MB": 50,
        "LOGGING": True,
        "WEBHOOK": "",
        "CHECK_INTERVAL": 60,
        "ATTACK_COOLDOWN_TTL": 300,
    },
    "CLOUDFLARE": {
        "EMAIL": "cf@example.com",
        "API_KEY": "1234567890",
        "ZONE_IDS": [],
    },
    "REDIS": {
        "HOST": "localhost",
        "PORT": 6379,
        "PASSWORD": "",
    },
}


class Config:
    def __init__(self):
        self._path = "config.yaml"
        if not self._exists():
            with open(self._path, "w", encoding="utf-8") as f:
                yaml.dump(_DEFAULT, f)
            raise ConfigNotFoundError(
                "config.yaml not found – a default file has been created. "
                "Please fill in your credentials and restart."
            )
        with open(self._path, "r", encoding="utf-8") as f:
            self._data = yaml.load(f, Loader=yaml.FullLoader)

    def get(self, section, key):
        """Return a value from the config."""
        return self._data[section][key]

    def _exists(self):
        try:
            with open(self._path, encoding="utf-8"):
                return True
        except FileNotFoundError:
            return False


_INSTANCE = None


def get_config():
    """Return the global Config singleton."""
    global _INSTANCE  # pylint: disable=global-statement
    if _INSTANCE is None:
        _INSTANCE = Config()
    return _INSTANCE
