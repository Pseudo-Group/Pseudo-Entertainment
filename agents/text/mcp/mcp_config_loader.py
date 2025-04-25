from typing import TypedDict

from yaml import safe_load


class McpConfig(TypedDict):
    news_host: str
    news_port: int
    news_url: str
    news_transport: str

    def __init__(self, config_path: str = "./agents/text/mcp/mcp_config.yml"):
        with open(config_path, "r") as f:
            config = safe_load(f)

        self.news_host = config["news"]["host"]
        self.news_port = config["news"]["port"]
        self.news_url = config["news"]["url"]
        self.news_transport = config["news"]["transport"]


mcp_config = McpConfig()
