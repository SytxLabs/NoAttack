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
                "HOST": "",
                "PORT": 6379,
                "PASSWORD": ""
            },
        }

    def get(self, section: str, key: str) -> str:
        """
        Get value from a config file
        :param section:
        :param key:
        :return:
        """
        with open(self.config, "r") as yf:
            data = yaml.load(yf, Loader=yaml.FullLoader)
            return data[section][key]

    def configExists(self):
        """
        Check if config file exists
        :return:
        """
        try:
            with open(self.config, "r") as yf:
                return True
        except FileNotFoundError:
            return False

    def createConfig(self):
        """
        Create a config file
        :return:
        """
        with open(self.config, "w") as yf:
            yaml.dump(self.config_data, yf)
            return True
