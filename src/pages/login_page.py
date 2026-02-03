"""LoginPage — interactions with the login screen."""

from __future__ import annotations

from typing import TYPE_CHECKING

from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver


class LoginPage(BasePage):
    """Page object for the application login screen."""

    # ── Locators ──────────────────────────────────────────────────────────

    USERNAME_FIELD: tuple[str, str] = (AppiumBy.ACCESSIBILITY_ID, "username_input")
    PASSWORD_FIELD: tuple[str, str] = (AppiumBy.ACCESSIBILITY_ID, "password_input")
    LOGIN_BUTTON: tuple[str, str] = (AppiumBy.ACCESSIBILITY_ID, "login_button")
    ERROR_MESSAGE: tuple[str, str] = (AppiumBy.ACCESSIBILITY_ID, "error_message")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ── Actions ───────────────────────────────────────────────────────────

    def login(self, username: str, password: str) -> None:
        """Enter credentials and tap the login button.

        Call this method, then instantiate the expected destination page
        in your test (e.g. ``HomePage`` on success).
        """
        self.type_text(self.USERNAME_FIELD, username)
        self.type_text(self.PASSWORD_FIELD, password)
        self.hide_keyboard()
        self.click(self.LOGIN_BUTTON)

    def get_error_message(self, timeout: int | None = None) -> str:
        """Return the visible error-message text after a failed login."""
        kwargs: dict[str, int] = {}
        if timeout is not None:
            kwargs["timeout"] = timeout
        return self.get_text(self.ERROR_MESSAGE, **kwargs)

    def is_login_button_displayed(self, timeout: int = 10) -> bool:
        """Return ``True`` if the login button is visible."""
        return self.is_displayed(self.LOGIN_BUTTON, timeout=timeout)
