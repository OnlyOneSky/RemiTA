"""WelcomePage — interactions with the visitor/welcome landing screen."""

from __future__ import annotations

from typing import TYPE_CHECKING

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.pages.base_page import BasePage

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver

# Full resource-id prefix for the company app.
_RID = "com.cathayholdings.vdrf.ta:id"


class WelcomePage(BasePage):
    """Page object for the app's visitor/welcome landing screen.

    This is the first screen after splash. It may show announcement
    dialogs that must be dismissed before interacting with the main
    welcome content.

    Main actions:
    - ``dismiss_startup_dialogs()`` — dismiss any announcement popups
    - ``tap_get_credit()`` — navigate to registration/credit application
    - ``tap_login()`` — navigate to the login screen
    """

    # ── Locators: Announcement dialog ─────────────────────────────────────

    DIALOG_CARD: tuple[str, str] = (AppiumBy.ID, f"{_RID}/card_dialog")
    DIALOG_TITLE: tuple[str, str] = (AppiumBy.ID, f"{_RID}/tv_title")
    DIALOG_CONTENT: tuple[str, str] = (AppiumBy.ID, f"{_RID}/tv_content")
    DIALOG_GOT_IT: tuple[str, str] = (AppiumBy.ID, f"{_RID}/positiveButton")
    DIALOG_PROGRESS: tuple[str, str] = (AppiumBy.ID, f"{_RID}/tv_progress")

    # ── Locators: Welcome/visitor screen ──────────────────────────────────

    VISITOR_CONTAINER: tuple[str, str] = (AppiumBy.ID, f"{_RID}/fcv_visitor")
    LANGUAGE_TOGGLE: tuple[str, str] = (AppiumBy.ID, f"{_RID}/tv_change_language")
    GET_CREDIT_BUTTON: tuple[str, str] = (AppiumBy.ID, f"{_RID}/btn_primary")
    LOGIN_BUTTON: tuple[str, str] = (AppiumBy.ID, f"{_RID}/btn_secondary")
    BANNER_VIEW: tuple[str, str] = (AppiumBy.ID, f"{_RID}/bannerView")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ── Dialog handling ───────────────────────────────────────────────────

    def is_dialog_displayed(self, timeout: int = 5) -> bool:
        """Return True if an announcement dialog is currently visible."""
        return self.is_displayed(self.DIALOG_CARD, timeout=timeout)

    def dismiss_dialog(self, timeout: int = 5) -> None:
        """Tap 'Got It' to dismiss the current announcement dialog."""
        self.click(self.DIALOG_GOT_IT, timeout=timeout)

    def dismiss_startup_dialogs(self, max_dialogs: int = 5, timeout: int = 10) -> int:
        """Dismiss all startup announcement dialogs.

        Returns the number of dialogs dismissed. Keeps tapping 'Got It'
        until no more dialogs appear (up to *max_dialogs* safety limit).
        """
        import time

        dismissed = 0
        for _ in range(max_dialogs):
            if self.is_dialog_displayed(timeout=timeout if dismissed == 0 else 3):
                self.dismiss_dialog()
                dismissed += 1
                time.sleep(0.5)  # Brief pause for next dialog to appear
            else:
                break
        return dismissed

    # ── Welcome screen actions ────────────────────────────────────────────

    def is_page_displayed(self, timeout: int = 15) -> bool:
        """Return True if the welcome/visitor screen is visible."""
        return self.is_displayed(self.GET_CREDIT_BUTTON, timeout=timeout)

    def tap_get_credit(self, timeout: int = 10) -> None:
        """Tap 'Get Credit' to start the registration/credit application flow."""
        self.click(self.GET_CREDIT_BUTTON, timeout=timeout)

    def tap_login(self, timeout: int = 10) -> None:
        """Tap 'Log In' to navigate to the login screen."""
        self.click(self.LOGIN_BUTTON, timeout=timeout)

    def get_language(self, timeout: int = 5) -> str:
        """Return the current language label (e.g. 'EN', 'VI')."""
        return self.get_text(self.LANGUAGE_TOGGLE, timeout=timeout)

    def tap_language_toggle(self, timeout: int = 5) -> None:
        """Tap the language toggle to switch display language."""
        self.click(self.LANGUAGE_TOGGLE, timeout=timeout)
