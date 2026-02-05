"""RegisterVerifyEmailPage — interactions with the email verification screen."""

from __future__ import annotations

from typing import TYPE_CHECKING

from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver

# Full resource-ID prefix for the app under test.
_PKG = "com.cathayholdings.vdrf.ta:id"


class RegisterVerifyEmailPage(BasePage):
    """Page object for the register — verify email screen."""

    # ── Locators ──────────────────────────────────────────────────────────

    TC_TITLE: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/tc_title")
    EMAIL_INPUT: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/ic_email")
    CTA_BUTTON: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/cta")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ── Actions ───────────────────────────────────────────────────────────

    def enter_email(self, email: str) -> None:
        """Type an email address into the InputComponent.

        The component (``ic_email``) wraps an ``EditText``; we locate
        the component first, then find the child input.
        """
        component = self.find_element(self.EMAIL_INPUT)
        edit_text = component.find_element(AppiumBy.CLASS_NAME, "android.widget.EditText")
        edit_text.clear()
        edit_text.send_keys(email)

    def tap_next(self) -> None:
        """Tap the CTA / Next button to submit the email."""
        self.click(self.CTA_BUTTON)

    # ── Assertions ────────────────────────────────────────────────────────

    def is_page_displayed(self, timeout: int = 10) -> bool:
        """Return ``True`` if the verify-email screen is visible."""
        return self.is_displayed(self.EMAIL_INPUT, timeout=timeout)
