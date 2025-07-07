import json
import os
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration."""

    chat_model: str = "gpt-3.5-turbo"
    system_prompt: str = ""


def load_config(path: str = "config.json") -> Config:
    """Load configuration from a JSON file and environment variables."""
    cfg = Config()
    data = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
    cfg.chat_model = os.getenv("CHAT_MODEL", data.get("chat_model", cfg.chat_model))
    cfg.system_prompt = os.getenv(
        "SYSTEM_PROMPT", data.get("system_prompt", cfg.system_prompt)
    )
    return cfg


# Load default config at import time
CONFIG = load_config()
