"""RegisterVerifyPhonePage — interactions with the phone number verification screen."""

from __future__ import annotations

from typing import TYPE_CHECKING

from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver

# Full resource-ID prefix for the app under test.
_PKG = "com.cathayholdings.vdrf.ta:id"


class RegisterVerifyPhonePage(BasePage):
    """Page object for the register — verify phone number screen."""

    # ── Locators ──────────────────────────────────────────────────────────

    TC_TITLE: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/tc_title")
    PHONE_INPUT: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/ic_phone_number")
    CTA_BUTTON: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/cta")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ── Actions ───────────────────────────────────────────────────────────

    def enter_phone_number(self, phone: str) -> None:
        """Type a phone number into the InputPhoneNumberComponent.

        The component (``ic_phone_number``) wraps an ``EditText``; we
        locate the component first, then find the child input.
        """
        component = self.find_element(self.PHONE_INPUT)
        edit_text = component.find_element(AppiumBy.CLASS_NAME, "android.widget.EditText")
        edit_text.clear()
        edit_text.send_keys(phone)

    def tap_next(self) -> None:
        """Tap the CTA / Next button to submit the phone number."""
        self.click(self.CTA_BUTTON)

    # ── Assertions ────────────────────────────────────────────────────────

    def is_page_displayed(self, timeout: int = 10) -> bool:
        """Return ``True`` if the verify-phone screen is visible."""
        return self.is_displayed(self.TC_TITLE, timeout=timeout)
