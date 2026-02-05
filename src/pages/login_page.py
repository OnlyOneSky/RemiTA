"""LoginPage — interactions with the login screen."""

from __future__ import annotations

from typing import TYPE_CHECKING

from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver

# Full resource-id prefix for the company app.
_RID = "com.cathayholdings.vdrf.ta:id"


class LoginPage(BasePage):
    """Page object for the application login screen."""

    # ── Locators (sample app — accessibility IDs) ─────────────────────────

    USERNAME_FIELD: tuple[str, str] = (AppiumBy.ACCESSIBILITY_ID, "username_input")
    PASSWORD_FIELD: tuple[str, str] = (AppiumBy.ACCESSIBILITY_ID, "password_input")
    LOGIN_BUTTON: tuple[str, str] = (AppiumBy.ACCESSIBILITY_ID, "login_button")
    REGISTER_BUTTON: tuple[str, str] = (AppiumBy.ID, "com.cathayholdings.vdrf.ta:id/tv_toolbar_option")
    ERROR_MESSAGE: tuple[str, str] = (AppiumBy.ACCESSIBILITY_ID, "error_message")

    # ── Locators (company app — resource IDs) ─────────────────────────────

    PHONE_FIELD: tuple[str, str] = (AppiumBy.ID, f"{_RID}/et_phone_number")
    PASSWORD_COMPANY_FIELD: tuple[str, str] = (AppiumBy.ID, f"{_RID}/et_possword")
    CTA_BUTTON: tuple[str, str] = (AppiumBy.ID, f"{_RID}/cta")
    REGISTER_BUTTON: tuple[str, str] = (AppiumBy.ID, f"{_RID}/tv_toolbar_option")

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

    def tap_register(self) -> None:
        """Tap the 'Register' link in the toolbar to navigate to registration."""
        self.click(self.REGISTER_BUTTON)

    def is_register_button_displayed(self, timeout: int = 15) -> bool:
        """Return ``True`` if the register toolbar button is visible."""
        return self.is_displayed(self.REGISTER_BUTTON, timeout=timeout)

    def get_error_message(self, timeout: int | None = None) -> str:
        """Return the visible error-message text after a failed login."""
        kwargs: dict[str, int] = {}
        if timeout is not None:
            kwargs["timeout"] = timeout
        return self.get_text(self.ERROR_MESSAGE, **kwargs)

    def is_login_button_displayed(self, timeout: int = 10) -> bool:
        """Return ``True`` if the login button is visible."""
        return self.is_displayed(self.LOGIN_BUTTON, timeout=timeout)
