import yaml

class Config:
    def __init__(self):
        self.config = "config.yaml"
        self.config_data = {
            "SETTINGS": {
                "MAX_INCOMING_TRAFFIC_MB": 50,
                "LOGGING": True,
                "WEBHOOK": "",
                "CHECK_INTERVAL": 60
            },
            "CLOUDFLARE": {
                "EMAIL": "cf@example.com",
                "API_KEY": "1234567890",
                "ZONE_IDS": []
            },
            "REDIS": {
                "HOST": "redis",
                "PORT": 6379,
                "PASSWORD": ""
            },
        }
        if not self.config_exists():
            self.create_config()

    def get(self, section: str, key: str) -> str:
        """
        Get a value from the config file.
        :param section: The configuration section name.
        :param key: The key within that section.
        :return: The corresponding value from the configuration.
        """
        with open(self.config, "r", encoding="utf-8") as yf:
            data = yaml.load(yf, Loader=yaml.FullLoader)
            return data[section][key]

    def config_exists(self) -> bool:
        """
        Check if the config file exists.
        :return: True if file exists, False otherwise.
        """
        try:
            with open(self.config, "r", encoding="utf-8"):
                return True
        except FileNotFoundError:
            return False

    def create_config(self) -> bool:
        """
        Create a config file using the default configuration data.
        :return: True if the config file was successfully created.
        """
        with open(self.config, "w", encoding="utf-8") as yf:
            yaml.dump(self.config_data, yf)
        return True
