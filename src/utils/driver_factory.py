"""DriverFactory — create Appium driver instances from config or DeviceInfo."""

from __future__ import annotations

import logging
from typing import Any

from appium import webdriver as appium_webdriver
from appium.options.common import AppiumOptions

from src.models.device_info import DeviceInfo
from src.utils.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class DriverFactory:
    """Factory for creating configured Appium ``WebDriver`` instances.

    Two creation paths:

    1. **Static** — from YAML config only (original behaviour)::

           driver = DriverFactory.get_driver("android")

    2. **Dynamic** — from a discovered ``DeviceInfo`` object::

           driver = DriverFactory.get_driver_for_device(device_info)
    """

    # ── Static: from YAML config ──────────────────────────────────

    @classmethod
    def get_driver(cls, platform: str) -> appium_webdriver.Remote:
        """Build a driver using only YAML config files.

        Parameters
        ----------
        platform:
            ``"android"`` or ``"ios"``.
        """
        merged_config = ConfigLoader.load_merged_config(platform)
        return cls._create_driver(merged_config, platform)

    # ── Dynamic: from DeviceInfo ──────────────────────────────────

    @classmethod
    def get_driver_for_device(cls, device: DeviceInfo) -> appium_webdriver.Remote:
        """Build a driver with capabilities injected from a discovered device.

        YAML configs are still loaded for defaults (app path, timeouts, etc.),
        but device-specific values (UDID, device name, platform version) are
        overridden from the ``DeviceInfo`` object.

        Parameters
        ----------
        device:
            A ``DeviceInfo`` instance from ``DeviceManager``.
        """
        merged_config = ConfigLoader.load_merged_config(device.platform)
        capabilities: dict[str, Any] = merged_config.get("capabilities", {})

        # Inject device-specific values into capabilities
        capabilities["platformName"] = device.platform.capitalize()

        appium_opts = capabilities.setdefault("appium:options", {})

        if device.platform == "android":
            appium_opts["deviceName"] = device.serial
            appium_opts["udid"] = device.serial
            if device.platform_version:
                appium_opts["platformVersion"] = device.platform_version
            # Use UiAutomator2 for Android
            appium_opts.setdefault("automationName", "UiAutomator2")

        elif device.platform == "ios":
            appium_opts["udid"] = device.serial
            appium_opts["deviceName"] = device.device_name
            if device.platform_version:
                appium_opts["platformVersion"] = device.platform_version
            # Use XCUITest for iOS
            appium_opts.setdefault("automationName", "XCUITest")

        logger.info(
            "Building driver for device: %s [%s]",
            device.display_name, device.serial,
        )

        return cls._create_driver(merged_config, device.platform)

    # ── Internal ──────────────────────────────────────────────────

    @classmethod
    def _create_driver(
        cls, config: dict[str, Any], platform: str
    ) -> appium_webdriver.Remote:
        """Shared logic for creating and configuring an Appium driver."""
        server_url: str = config.get("appium", {}).get(
            "server_url", "http://127.0.0.1:4723"
        )
        capabilities: dict[str, Any] = config.get("capabilities", {})
        implicit_wait: int = config.get("timeouts", {}).get("implicit_wait", 10)

        logger.info("Creating %s driver → %s", platform, server_url)
        logger.debug("Capabilities: %s", capabilities)

        options = AppiumOptions()
        options.load_capabilities(capabilities)

        driver = appium_webdriver.Remote(
            command_executor=server_url,
            options=options,
        )

        driver.implicitly_wait(implicit_wait)

        logger.info("Driver session created: %s", driver.session_id)
        return driver
