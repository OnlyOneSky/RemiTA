"""RegisterCreatePasswordPage — interactions with the create-password screen."""

from __future__ import annotations

from typing import TYPE_CHECKING

from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver

# Full resource-ID prefix for the app under test.
_PKG = "com.cathayholdings.vdrf.ta:id"


class RegisterCreatePasswordPage(BasePage):
    """Page object for the register — create password screen.

    The password component (``InputPosswordTwoEndIconSetComponent``) contains
    **two** ``EditText`` children: one for the new password and one for
    the confirmation.
    """

    # ── Locators ──────────────────────────────────────────────────────────

    TC_TITLE: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/tc_title")
    PASSWORD_INPUT: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/ic_possword_set")
    CTA_BUTTON: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/cta")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ── Actions ───────────────────────────────────────────────────────────

    def enter_password(self, password: str) -> None:
        """Fill both password fields (new + confirm) with *password*.

        The component ``ic_possword_set`` contains two ``EditText`` children.
        """
        component = self.find_element(self.PASSWORD_INPUT)
        edit_texts = component.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")

        # First field: new password
        edit_texts[0].clear()
        edit_texts[0].send_keys(password)

        # Second field: confirm password
        edit_texts[1].clear()
        edit_texts[1].send_keys(password)

    def tap_next(self) -> None:
        """Tap the CTA / Next button to submit the password."""
        self.click(self.CTA_BUTTON)

    # ── Assertions ────────────────────────────────────────────────────────

    def is_page_displayed(self, timeout: int = 10) -> bool:
        """Return ``True`` if the create-password screen is visible."""
        return self.is_displayed(self.PASSWORD_INPUT, timeout=timeout)
