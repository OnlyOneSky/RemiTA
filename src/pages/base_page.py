"""BasePage — shared actions and helpers for all page objects."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.utils.config_loader import ConfigLoader

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement

# Default timeout pulled from settings; fallback to 15s if not configured.
_settings = ConfigLoader.load_settings()
DEFAULT_TIMEOUT: int = _settings.get("timeouts", {}).get("explicit_wait", 15)
SCREENSHOT_DIR: str = _settings.get("screenshots", {}).get("output_dir", "reports/screenshots")


class BasePage:
    """Base class that every page object inherits from.

    Provides common helpers for finding elements, interacting with them,
    swiping, taking screenshots, and navigating.
    """

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    # ── Element helpers ───────────────────────────────────────────────────

    def find_element(self, locator: tuple[str, str], timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        """Wait for an element to be present and return it."""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))

    def click(self, locator: tuple[str, str], timeout: int = DEFAULT_TIMEOUT) -> None:
        """Wait for an element to be clickable, then tap it."""
        wait = WebDriverWait(self.driver, timeout)
        element = wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def type_text(self, locator: tuple[str, str], text: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Clear the field and type *text* into it."""
        element = self.find_element(locator, timeout)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple[str, str], timeout: int = DEFAULT_TIMEOUT) -> str:
        """Return the visible text of an element."""
        element = self.find_element(locator, timeout)
        return element.text

    def is_displayed(self, locator: tuple[str, str], timeout: int = DEFAULT_TIMEOUT) -> bool:
        """Return ``True`` if the element is visible within *timeout*."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def wait_for_element(self, locator: tuple[str, str], timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        """Explicitly wait for an element to become visible and return it."""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.visibility_of_element_located(locator))

    # ── Swipe gestures ────────────────────────────────────────────────────

    def _swipe(self, start_x: float, start_y: float, end_x: float, end_y: float, duration: int = 800) -> None:
        """Perform a swipe gesture from one point to another."""
        self.driver.swipe(int(start_x), int(start_y), int(end_x), int(end_y), duration)

    def _get_screen_size(self) -> tuple[int, int]:
        """Return (width, height) of the current screen."""
        size = self.driver.get_window_size()
        return size["width"], size["height"]

    def swipe_up(self, duration: int = 800) -> None:
        """Swipe from bottom-center to top-center."""
        w, h = self._get_screen_size()
        self._swipe(w / 2, h * 0.8, w / 2, h * 0.2, duration)

    def swipe_down(self, duration: int = 800) -> None:
        """Swipe from top-center to bottom-center."""
        w, h = self._get_screen_size()
        self._swipe(w / 2, h * 0.2, w / 2, h * 0.8, duration)

    def swipe_left(self, duration: int = 800) -> None:
        """Swipe from right-center to left-center."""
        w, h = self._get_screen_size()
        self._swipe(w * 0.8, h / 2, w * 0.2, h / 2, duration)

    def swipe_right(self, duration: int = 800) -> None:
        """Swipe from left-center to right-center."""
        w, h = self._get_screen_size()
        self._swipe(w * 0.2, h / 2, w * 0.8, h / 2, duration)

    # ── Screenshots ───────────────────────────────────────────────────────

    def take_screenshot(self, name: str) -> str:
        """Save a screenshot and return the file path."""
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(SCREENSHOT_DIR, f"{name}_{timestamp}.png")
        self.driver.save_screenshot(file_path)
        return file_path

    # ── Navigation ────────────────────────────────────────────────────────

    def go_back(self) -> None:
        """Press the device back button."""
        self.driver.back()

    def hide_keyboard(self) -> None:
        """Dismiss the on-screen keyboard if visible."""
        try:
            self.driver.hide_keyboard()
        except Exception:  # noqa: BLE001 — keyboard may not be present
            pass
