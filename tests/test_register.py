"""Registration test suite — validates the full register flow."""

from __future__ import annotations

from typing import TYPE_CHECKING

import allure
import pytest

from src.pages.register_create_password_page import RegisterCreatePasswordPage
from src.pages.register_otp_page import RegisterOtpPage
from src.pages.register_success_page import RegisterSuccessPage
from src.pages.register_verify_email_page import RegisterVerifyEmailPage
from src.pages.register_verify_phone_page import RegisterVerifyPhonePage
from src.pages.welcome_page import WelcomePage

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver

    from src.utils.wiremock_client import WireMockClient

# ── Test data ─────────────────────────────────────────────────────────────────

PHONE = "987123789"
OTP = "123456"
EMAIL = "test@gmail.com"
PASSWORD = "Test@1234"

# ── WireMock mapping paths ────────────────────────────────────────────────────

_STUB_SEND_PHONE_OTP = "wiremock/mappings/register_send_phone_otp.json"
_STUB_VERIFY_PHONE_OTP = "wiremock/mappings/register_verify_phone_otp.json"
_STUB_SEND_EMAIL_OTP = "wiremock/mappings/register_send_email_otp.json"
_STUB_VERIFY_EMAIL_OTP = "wiremock/mappings/register_verify_email_otp.json"
_STUB_CREATE_PASSWORD = "wiremock/mappings/register_create_password.json"


@allure.epic("Registration")
@allure.feature("Register")
class TestRegister:
    """Tests for the user registration flow."""

    @pytest.mark.smoke
    @pytest.mark.regression
    @allure.story("Successful Registration")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Complete registration happy path")
    @allure.description(
        "Verify the full registration flow: phone verification → phone OTP → "
        "email verification → email OTP → create password → success screen."
    )
    def test_successful_registration(self, driver: WebDriver, wiremock: WireMockClient) -> None:
        """A new user should be able to register and reach the success screen."""
        with allure.step("Set up WireMock stubs for the full registration flow"):
            wiremock.load_mapping_from_file(_STUB_SEND_PHONE_OTP)
            wiremock.load_mapping_from_file(_STUB_VERIFY_PHONE_OTP)
            wiremock.load_mapping_from_file(_STUB_SEND_EMAIL_OTP)
            wiremock.load_mapping_from_file(_STUB_VERIFY_EMAIL_OTP)
            wiremock.load_mapping_from_file(_STUB_CREATE_PASSWORD)

        welcome_page = WelcomePage(driver)

        with allure.step("Dismiss startup announcement dialogs"):
            welcome_page.dismiss_startup_dialogs()

        with allure.step("Navigate through welcome → intro → T&C to registration"):
            assert welcome_page.is_page_displayed(), "Welcome screen did not appear"
            welcome_page.navigate_to_registration()

        verify_phone_page = RegisterVerifyPhonePage(driver)

        with allure.step(f"Enter phone number '{PHONE}' and tap Next"):
            assert verify_phone_page.is_page_displayed(), "Verify phone screen did not appear"
            verify_phone_page.enter_phone_number(PHONE)
            verify_phone_page.tap_next()

        phone_otp_page = RegisterOtpPage(driver)

        with allure.step("Enter phone OTP and tap Verify"):
            assert phone_otp_page.is_page_displayed(), "Phone OTP screen did not appear"
            phone_otp_page.enter_otp(OTP)
            phone_otp_page.tap_verify()

        verify_email_page = RegisterVerifyEmailPage(driver)

        with allure.step(f"Enter email '{EMAIL}' and tap Next"):
            assert verify_email_page.is_page_displayed(), "Verify email screen did not appear"
            verify_email_page.enter_email(EMAIL)
            verify_email_page.tap_next()

        email_otp_page = RegisterOtpPage(driver)

        with allure.step("Enter email OTP and tap Verify"):
            assert email_otp_page.is_page_displayed(), "Email OTP screen did not appear"
            email_otp_page.enter_otp(OTP)
            email_otp_page.tap_verify()

        create_password_page = RegisterCreatePasswordPage(driver)

        with allure.step("Enter password and tap Next"):
            assert create_password_page.is_page_displayed(), "Create password screen did not appear"
            create_password_page.enter_password(PASSWORD)
            create_password_page.tap_next()

        success_page = RegisterSuccessPage(driver)

        with allure.step("Verify success screen is displayed"):
            assert success_page.is_page_displayed(), "Registration success screen did not appear"

        with allure.step("Verify success title contains 'Hooray!'"):
            title = success_page.get_title()
            assert "Hooray" in title, f"Expected 'Hooray!' in title, got: '{title}'"

    @pytest.mark.regression
    @allure.story("Phone OTP Sent")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Phone OTP screen appears after submitting phone number")
    @allure.description(
        "Verify that after entering a phone number and tapping Next, "
        "the OTP verification screen is displayed."
    )
    def test_register_phone_otp_sent(self, driver: WebDriver, wiremock: WireMockClient) -> None:
        """Submitting a phone number should navigate to the OTP screen."""
        with allure.step("Set up WireMock stub for sending phone OTP"):
            wiremock.load_mapping_from_file(_STUB_SEND_PHONE_OTP)

        welcome_page = WelcomePage(driver)

        with allure.step("Dismiss startup announcement dialogs"):
            welcome_page.dismiss_startup_dialogs()

        with allure.step("Navigate through welcome → intro → T&C to registration"):
            assert welcome_page.is_page_displayed(), "Welcome screen did not appear"
            welcome_page.navigate_to_registration()

        verify_phone_page = RegisterVerifyPhonePage(driver)

        with allure.step(f"Enter phone number '{PHONE}' and tap Next"):
            assert verify_phone_page.is_page_displayed(), "Verify phone screen did not appear"
            verify_phone_page.enter_phone_number(PHONE)
            verify_phone_page.tap_next()

        otp_page = RegisterOtpPage(driver)

        with allure.step("Verify OTP screen is displayed"):
            assert otp_page.is_page_displayed(), "Phone OTP screen did not appear after submitting phone number"

    @pytest.mark.regression
    @allure.story("Email Verification Displayed")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Email verification screen appears after phone OTP verification")
    @allure.description(
        "Verify that after completing phone verification, "
        "the email verification screen is displayed."
    )
    def test_register_verify_email_displayed(self, driver: WebDriver, wiremock: WireMockClient) -> None:
        """After phone OTP verification, the email verification screen should appear."""
        with allure.step("Set up WireMock stubs for phone verification"):
            wiremock.load_mapping_from_file(_STUB_SEND_PHONE_OTP)
            wiremock.load_mapping_from_file(_STUB_VERIFY_PHONE_OTP)

        welcome_page = WelcomePage(driver)

        with allure.step("Dismiss startup announcement dialogs"):
            welcome_page.dismiss_startup_dialogs()

        with allure.step("Navigate through welcome → intro → T&C to registration"):
            assert welcome_page.is_page_displayed(), "Welcome screen did not appear"
            welcome_page.navigate_to_registration()

        verify_phone_page = RegisterVerifyPhonePage(driver)

        with allure.step(f"Enter phone number '{PHONE}' and tap Next"):
            assert verify_phone_page.is_page_displayed(), "Verify phone screen did not appear"
            verify_phone_page.enter_phone_number(PHONE)
            verify_phone_page.tap_next()

        otp_page = RegisterOtpPage(driver)

        with allure.step("Enter phone OTP and tap Verify"):
            assert otp_page.is_page_displayed(), "Phone OTP screen did not appear"
            otp_page.enter_otp(OTP)
            otp_page.tap_verify()

        verify_email_page = RegisterVerifyEmailPage(driver)

        with allure.step("Verify email verification screen is displayed"):
            assert verify_email_page.is_page_displayed(), (
                "Email verification screen did not appear after phone OTP verification"
            )
