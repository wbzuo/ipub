"""Configuration management for ipub."""

from pathlib import Path
import yaml


DEFAULT_CONFIG = {
    "project": "my-notes",
    "llm": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
    },
    "scan": {
        "extensions": [".md", ".txt"],
        "ignore": ["node_modules", ".git", ".ipub", "__pycache__"],
        "min_words": 100,
    },
    "platforms": {
        "blog": {"format": "markdown", "max_length": None},
        "csdn": {"format": "markdown", "max_length": None},
        "zhihu": {"format": "markdown", "max_length": None},
        "feishu": {"format": "markdown", "max_length": None},
    },
    "feishu": {
        "app_id": "",
        "app_secret": "",
    },
    "style": {
        "tone": "technical",
        "avoid_phrases": ["众所周知", "值得一提的是", "本文将"],
        "language": "zh",
    },
}

CONFIG_FILENAME = "ipub.yaml"


def find_config() -> Path | None:
    """Find ipub.yaml in current or parent directories."""
    current = Path.cwd()
    while current != current.parent:
        config_path = current / CONFIG_FILENAME
        if config_path.exists():
            return config_path
        current = current.parent
    return None


def load_config() -> dict:
    """Load configuration, falling back to defaults."""
    config_path = find_config()
    if config_path is None:
        return DEFAULT_CONFIG.copy()
    with open(config_path) as f:
        user_config = yaml.safe_load(f) or {}
    config = DEFAULT_CONFIG.copy()
    _deep_merge(config, user_config)
    return config


def init_config() -> Path:
    """Create a default ipub.yaml in the current directory."""
    config_path = Path.cwd() / CONFIG_FILENAME
    if config_path.exists():
        return config_path
    with open(config_path, "w") as f:
        yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return config_path


def _deep_merge(base: dict, override: dict):
    """Merge override into base recursively."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
