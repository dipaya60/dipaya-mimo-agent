"""
Configuration Management
Centralized config with YAML, env vars, and CLI overrides.
"""

import os
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any


CONFIG_DIR = Path(__file__).parent.parent / "config"


@dataclass
class MiMoConfig:
    """MiMo API configuration."""
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "mimo-v2.5-pro"
    max_tokens: int = 4096
    temperature: float = 0.7
    json_mode: bool = False
    max_retries: int = 3
    timeout: int = 60


@dataclass
class APIKeys:
    """External API keys."""
    coingecko_api_key: str = ""          # FREE: no key needed for basic
    etherscan_api_key: str = ""          # FREE tier available
    polygonscan_api_key: str = ""        # FREE tier available
    bscscan_api_key: str = ""            # FREE tier available
    arbiscan_api_key: str = ""           # FREE tier available
    snowtrace_api_key: str = ""          # FREE tier available
    solscan_api_key: str = ""            # FREE tier available
    moralis_api_key: str = ""            # FREE tier available
    alchemy_api_key: str = ""            # FREE tier available
    whale_alert_api_key: str = ""        # PAID: whale-alert.io
    glassnode_api_key: str = ""          # PAID: glassnode.com
    dune_api_key: str = ""               # FREE tier available
    twitter_bearer_token: str = ""       # PAID: X API
    telegram_bot_token: str = ""         # FREE: Telegram Bot API


@dataclass
class AppConfig:
    """Main application configuration."""
    mimo: MiMoConfig = field(default_factory=MiMoConfig)
    api_keys: APIKeys = field(default_factory=APIKeys)
    log_level: str = "INFO"
    demo_mode: bool = True
    output_format: str = "rich"  # rich, json, plain


def load_config(config_path: Optional[str] = None, cli_overrides: Optional[Dict[str, Any]] = None) -> AppConfig:
    """Load configuration from YAML + env vars + CLI overrides."""
    config = AppConfig()

    # 1. Load YAML defaults
    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
    else:
        default_path = CONFIG_DIR / "default.yaml"
        if default_path.exists():
            with open(default_path) as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}

    # 2. Apply YAML values
    if "mimo" in data:
        for k, v in data["mimo"].items():
            if hasattr(config.mimo, k):
                setattr(config.mimo, k, v)
    if "log_level" in data:
        config.log_level = data["log_level"]
    if "demo_mode" in data:
        config.demo_mode = data["demo_mode"]

    # 3. Override with environment variables (highest priority for secrets)
    env_map = {
        "MIMO_API_KEY": ("mimo", "api_key"),
        "MIMO_BASE_URL": ("mimo", "base_url"),
        "MIMO_MODEL": ("mimo", "model"),
        "COINGECKO_API_KEY": ("api_keys", "coingecko_api_key"),
        "ETHERSCAN_API_KEY": ("api_keys", "etherscan_api_key"),
        "POLYGONSCAN_API_KEY": ("api_keys", "polygonscan_api_key"),
        "BSCSCAN_API_KEY": ("api_keys", "bscscan_api_key"),
        "ARBISCAN_API_KEY": ("api_keys", "arbiscan_api_key"),
        "SNOWTRACE_API_KEY": ("api_keys", "snowtrace_api_key"),
        "SOLSCAN_API_KEY": ("api_keys", "solscan_api_key"),
        "MORALIS_API_KEY": ("api_keys", "moralis_api_key"),
        "ALCHEMY_API_KEY": ("api_keys", "alchemy_api_key"),
        "WHALE_ALERT_API_KEY": ("api_keys", "whale_alert_api_key"),
        "GLASSNODE_API_KEY": ("api_keys", "glassnode_api_key"),
        "DUNE_API_KEY": ("api_keys", "dune_api_key"),
        "TWITTER_BEARER_TOKEN": ("api_keys", "twitter_bearer_token"),
        "TELEGRAM_BOT_TOKEN": ("api_keys", "telegram_bot_token"),
    }
    for env_var, (section, key) in env_map.items():
        val = os.environ.get(env_var)
        if val:
            setattr(getattr(config, section), key, val)

    # 4. CLI overrides
    if cli_overrides:
        for k, v in cli_overrides.items():
            if "." in k:
                section, attr = k.split(".", 1)
                obj = getattr(config, section, None)
                if obj and hasattr(obj, attr):
                    setattr(obj, attr, v)
            elif hasattr(config, k):
                setattr(config, k, v)

    return config
