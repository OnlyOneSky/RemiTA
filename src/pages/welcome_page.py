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

    # ── Locators: Intro popup (after Get Credit) ──────────────────────────

    INTRO_CLOSE_BUTTON: tuple[str, str] = (AppiumBy.ID, f"{_RID}/ib_close")
    INTRO_TITLE: tuple[str, str] = (AppiumBy.ID, f"{_RID}/title")
    BECOME_MEMBER_BUTTON: tuple[str, str] = (AppiumBy.ID, f"{_RID}/btn_primary")

    # ── Locators: Terms & Conditions popup ────────────────────────────────

    TERMS_DIALOG_TITLE: tuple[str, str] = (AppiumBy.ID, f"{_RID}/tv_dialog_title")
    TERMS_LIST: tuple[str, str] = (AppiumBy.ID, f"{_RID}/rv_terms")
    AGREE_TERMS_BUTTON: tuple[str, str] = (AppiumBy.ID, f"{_RID}/btn_primary")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ── Dialog handling ───────────────────────────────────────────────────

    def is_dialog_displayed(self, timeout: int = 5) -> bool:
        """Return True if an announcement dialog is currently visible."""
        return self.is_displayed(self.DIALOG_CARD, timeout=timeout)

    def dismiss_dialog(self, timeout: int = 5) -> None:
        """Tap 'Got It' to dismiss the current announcement dialog."""
        self.click(self.DIALOG_GOT_IT, timeout=timeout)

    def dismiss_startup_dialogs(self, max_dialogs: int = 5, timeout: int = 3) -> int:
        """Dismiss all startup announcement dialogs.

        Returns the number of dialogs dismissed. Keeps tapping 'Got It'
        until no more dialogs appear (up to *max_dialogs* safety limit).
        """
        import time

        dismissed = 0
        for _ in range(max_dialogs):
            if self.is_dialog_displayed(timeout=timeout):
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

    # ── Intro popup actions ───────────────────────────────────────────────

    def is_intro_popup_displayed(self, timeout: int = 10) -> bool:
        """Return True if the intro popup (Become a Member) is visible."""
        return self.is_displayed(self.INTRO_TITLE, timeout=timeout)

    def tap_become_member(self, timeout: int = 10) -> None:
        """Tap 'Become a Member' on the intro popup."""
        self.click(self.BECOME_MEMBER_BUTTON, timeout=timeout)

    # ── Terms & Conditions popup actions ──────────────────────────────────

    def is_terms_popup_displayed(self, timeout: int = 10) -> bool:
        """Return True if the Terms & Conditions popup is visible."""
        return self.is_displayed(self.TERMS_DIALOG_TITLE, timeout=timeout)

    def tap_agree_terms(self, timeout: int = 10) -> None:
        """Tap 'Agree' on the Terms & Conditions popup."""
        self.click(self.AGREE_TERMS_BUTTON, timeout=timeout)

    # ── Full registration navigation ──────────────────────────────────────

    def navigate_to_registration(self, timeout: int = 10) -> None:
        """Complete the full navigation from welcome screen to registration.

        Handles: Get Credit → Intro popup → T&C popup → Verify Phone screen.
        
        Both the intro popup and T&C popup use btn_primary as the action button,
        so we tap it twice after the initial Get Credit tap.
        """
        import time

        # Step 1: Tap "Get Credit" on welcome screen
        self.tap_get_credit(timeout=timeout)
        time.sleep(2)  # Wait for intro popup to appear

        # Step 2: Tap "Become a Member" on intro popup
        self.tap_become_member(timeout=timeout)
        time.sleep(2)  # Wait for T&C popup to appear

        # Step 3: Tap "I Agree" on T&C popup
        self.tap_agree_terms(timeout=timeout)
        time.sleep(1)  # Wait for verify phone screen to load
