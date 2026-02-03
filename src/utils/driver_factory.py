"""Appium driver factory — creates drivers for Android or iOS."""

from __future__ import annotations

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.webdriver import WebDriver

from src.utils.config_loader import get_config


class DriverFactory:
    """Build an Appium WebDriver from YAML config."""

    @classmethod
    def get_driver(cls, platform: str) -> WebDriver:
        """Create and return an Appium driver for the given platform.

        Args:
            platform: 'android' or 'ios'

        Returns:
            Configured Appium WebDriver instance.
        """
        config = get_config(platform)
        settings = config["settings"]
        caps = config["capabilities"]

        server_url = settings["appium"]["server_url"]
        appium_opts = caps.get("appium:options", {})

        if platform.lower() == "android":
            options = UiAutomator2Options()
        elif platform.lower() == "ios":
            options = XCUITestOptions()
        else:
            raise ValueError(f"Unsupported platform: {platform}")

        # Set platform name
        options.platform_name = caps.get("platformName", platform)

        # Apply all appium:options from the YAML config
        for key, value in appium_opts.items():
            options.set_capability(f"appium:{key}", value)

        driver = webdriver.Remote(server_url, options=options)

        # Apply timeouts from settings
        timeouts = settings.get("timeouts", {})
        implicit = timeouts.get("implicit_wait", 10)
        driver.implicitly_wait(implicit)

        return driver
