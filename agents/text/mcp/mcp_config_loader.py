import os
from dataclasses import dataclass

from yaml import safe_load


@dataclass
class McpConfig:
    news_host: str
    news_port: int
    news_url: str
    news_transport: str

    @classmethod
    def from_yaml(cls, config_path: str = "mcp_config.yml") -> "McpConfig":
        # Get the directory containing this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct absolute path to config file
        config_path = os.path.join(current_dir, config_path)

        with open(config_path, "r") as f:
            config = safe_load(f)

        return cls(
            news_host=config["news"]["host"],
            news_port=config["news"]["port"],
            news_url=config["news"]["url"],
            news_transport=config["news"]["transport"],
        )


mcp_config = McpConfig.from_yaml()
