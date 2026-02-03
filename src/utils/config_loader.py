"""ConfigLoader — YAML configuration loading and merging."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

# Load .env from project root (if present) so env vars are available early.
load_dotenv()

# Resolve project root (two levels up from this file: src/utils/ → project root).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_DIR = _PROJECT_ROOT / "config"


class ConfigLoader:
    """Load and merge YAML configuration files.

    Priority (highest → lowest):
        1. Environment variables
        2. Platform config (android.yaml / ios.yaml)
        3. General settings (settings.yaml)
    """

    @staticmethod
    def _load_yaml(file_path: Path) -> dict[str, Any]:
        """Read a YAML file and return its contents as a dict."""
        with open(file_path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data if isinstance(data, dict) else {}

    @classmethod
    def load_settings(cls) -> dict[str, Any]:
        """Load ``config/settings.yaml``."""
        return cls._load_yaml(_CONFIG_DIR / "settings.yaml")

    @classmethod
    def load_platform_config(cls, platform: str) -> dict[str, Any]:
        """Load the platform-specific config (``android.yaml`` or ``ios.yaml``)."""
        filename = f"{platform.lower()}.yaml"
        path = _CONFIG_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Platform config not found: {path}")
        return cls._load_yaml(path)

    @classmethod
    def load_merged_config(cls, platform: str) -> dict[str, Any]:
        """Merge ``settings.yaml`` with the platform config.

        Keys in the platform file override keys in settings when they
        share the same top-level name.  Environment variable overrides
        are applied last:

        * ``APPIUM_URL``   → ``appium.server_url``
        * ``WIREMOCK_URL`` → ``wiremock.base_url``
        """
        settings = cls.load_settings()
        platform_cfg = cls.load_platform_config(platform)

        merged: dict[str, Any] = {**settings, **platform_cfg}

        # Environment-variable overrides
        env_appium_url = os.getenv("APPIUM_URL")
        if env_appium_url:
            merged.setdefault("appium", {})["server_url"] = env_appium_url

        env_wiremock_url = os.getenv("WIREMOCK_URL")
        if env_wiremock_url:
            merged.setdefault("wiremock", {})["base_url"] = env_wiremock_url

        return merged

    @classmethod
    def resolve_path(cls, relative_path: str) -> Path:
        """Resolve a path relative to the project root.

        If the path is already absolute, return it as-is.
        """
        p = Path(relative_path)
        if p.is_absolute():
            return p
        return _PROJECT_ROOT / p
