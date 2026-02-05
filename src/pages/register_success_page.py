"""RegisterSuccessPage — interactions with the registration success screen."""

from __future__ import annotations

from typing import TYPE_CHECKING

from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver

# Full resource-ID prefix for the app under test.
_PKG = "com.cathayholdings.vdrf.ta:id"


class RegisterSuccessPage(BasePage):
    """Page object for the 'Hooray!' registration success screen."""

    # ── Locators ──────────────────────────────────────────────────────────

    RESULT_COMPONENT: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/resultComponent")
    GET_CREDIT_BUTTON: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/btn_primary")
    EXPLORE_BUTTON: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/btn_secondary")
    TITLE_TEXT: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/tv_title")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ── Actions ───────────────────────────────────────────────────────────

    def tap_get_credit(self) -> None:
        """Tap the 'Get My Credit!' primary button."""
        self.click(self.GET_CREDIT_BUTTON)

    def tap_explore(self) -> None:
        """Tap the secondary / explore button."""
        self.click(self.EXPLORE_BUTTON)

    def get_title(self) -> str:
        """Return the title text (expected to contain 'Hooray!')."""
        return self.get_text(self.TITLE_TEXT)

    # ── Assertions ────────────────────────────────────────────────────────

    def is_page_displayed(self, timeout: int = 10) -> bool:
        """Return ``True`` if the success screen is visible."""
        return self.is_displayed(self.RESULT_COMPONENT, timeout=timeout)
