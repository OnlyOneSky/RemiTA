"""YAML config loader — merges settings with platform-specific config."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"


def load_yaml(file_path: Path) -> dict[str, Any]:
    """Load a single YAML file and return its contents as a dict."""
    with open(file_path, "r") as f:
        return yaml.safe_load(f) or {}


def load_settings() -> dict[str, Any]:
    """Load the shared settings.yaml."""
    return load_yaml(CONFIG_DIR / "settings.yaml")


def load_platform_config(platform: str) -> dict[str, Any]:
    """Load platform-specific config (android.yaml or ios.yaml)."""
    filename = f"{platform.lower()}.yaml"
    path = CONFIG_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Platform config not found: {path}")
    return load_yaml(path)


def get_config(platform: str) -> dict[str, Any]:
    """Return merged config: shared settings + platform capabilities."""
    settings = load_settings()
    platform_config = load_platform_config(platform)
    return {
        "settings": settings,
        "capabilities": platform_config,
    }
