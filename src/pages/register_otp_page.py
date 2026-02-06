"""RegisterOtpPage — shared page object for phone and email OTP screens."""

from __future__ import annotations

from typing import TYPE_CHECKING

from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver

# Full resource-ID prefix for the app under test.
_PKG = "com.cathayholdings.vdrf.ta:id"


class RegisterOtpPage(BasePage):
    """Page object for the OTP verification screen (phone or email)."""

    # ── Locators ──────────────────────────────────────────────────────────

    OTP_DESC: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/tv_otp_desc")
    PHONE_NUMBER_DISPLAY: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/tv_phone_number")
    PIN_INPUT: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/pcc_pin")
    CTA_BUTTON: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/cta")
    HELP_LINK: tuple[str, str] = (AppiumBy.ID, f"{_PKG}/btn_help")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ── Actions ───────────────────────────────────────────────────────────

    def enter_otp(self, otp: str) -> None:
        """Enter a 6-digit OTP into the PinCodeComponent.

        Tries multiple approaches:
        1. Find individual EditText children and enter one digit each
        2. Click the component and type the full OTP
        3. Use Android keycode events
        """
        import time
        from appium.webdriver.extensions.android.nativekey import AndroidKey
        
        component = self.find_element(self.PIN_INPUT)
        
        # Try to find individual digit fields
        digit_fields = component.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
        
        if digit_fields and len(digit_fields) >= len(otp):
            # Method 1: Individual fields
            print(f"    >>> OTP: Using individual fields method ({len(digit_fields)} fields)")
            for i, digit in enumerate(otp):
                digit_fields[i].click()
                digit_fields[i].send_keys(digit)
                time.sleep(0.1)  # Small delay between digits
        else:
            # Method 2: Click and type directly using keyboard
            print(f"    >>> OTP: Using keycode method (found {len(digit_fields) if digit_fields else 0} fields)")
            component.click()
            time.sleep(0.5)
            
            # Type each digit with keypress
            for digit in otp:
                key_code = getattr(AndroidKey, f"DIGIT_{digit}")
                self.driver.press_keycode(key_code)
                time.sleep(0.15)  # Slightly longer delay
        
        # Wait for any auto-submit or UI update after OTP entry
        print("    >>> OTP: Entry complete, waiting 2s for app response...")
        time.sleep(2)

    def tap_verify(self) -> None:
        """Tap the primary CTA (Verify) button."""
        print("    >>> OTP: Tapping Verify button...")
        self.click(self.CTA_BUTTON)
        print("    >>> OTP: Verify tapped, waiting 2s for API response...")
        import time
        time.sleep(2)

    def tap_resend(self) -> None:
        """Tap the resend / secondary CTA button (same element, text toggles)."""
        self.click(self.CTA_BUTTON)

    def get_otp_description(self) -> str:
        """Return the OTP description text (e.g. 'We sent a code to …')."""
        return self.get_text(self.OTP_DESC)

    # ── Assertions ────────────────────────────────────────────────────────

    def is_page_displayed(self, timeout: int = 10) -> bool:
        """Return ``True`` if the OTP screen is visible."""
        return self.is_displayed(self.PIN_INPUT, timeout=timeout)
