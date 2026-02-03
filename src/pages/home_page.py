"""HomePage — interactions with the home / dashboard screen."""

from __future__ import annotations

from typing import TYPE_CHECKING

from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver


class HomePage(BasePage):
    """Page object for the application home screen (post-login)."""

    # ── Locators ──────────────────────────────────────────────────────────

    WELCOME_MESSAGE: tuple[str, str] = (AppiumBy.ACCESSIBILITY_ID, "welcome_message")
    MENU_BUTTON: tuple[str, str] = (AppiumBy.ACCESSIBILITY_ID, "menu_button")
    LOGOUT_BUTTON: tuple[str, str] = (AppiumBy.ACCESSIBILITY_ID, "logout_button")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ── Actions ───────────────────────────────────────────────────────────

    def get_welcome_message(self, timeout: int | None = None) -> str:
        """Return the text of the welcome banner."""
        kwargs: dict[str, int] = {}
        if timeout is not None:
            kwargs["timeout"] = timeout
        return self.get_text(self.WELCOME_MESSAGE, **kwargs)

    def tap_menu(self) -> None:
        """Open the side / hamburger menu."""
        self.click(self.MENU_BUTTON)

    def logout(self) -> None:
        """Tap the logout button (may require the menu to be open first)."""
        self.click(self.LOGOUT_BUTTON)

    def is_home_displayed(self, timeout: int = 15) -> bool:
        """Return ``True`` if the welcome message is visible (indicates home screen loaded)."""
        return self.is_displayed(self.WELCOME_MESSAGE, timeout=timeout)
