"""Login test suite — validates authentication flows."""

from __future__ import annotations

from typing import TYPE_CHECKING

import allure
import pytest

from src.models.user import User
from src.pages.home_page import HomePage
from src.pages.login_page import LoginPage

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver

    from src.utils.wiremock_client import WireMockClient

# ── Test data ─────────────────────────────────────────────────────────────────

VALID_USER = User(username="valid_user", password="valid_pass", expected_name="Remi Chen")
INVALID_USER = User(username="invalid_user", password="wrong_pass")


@allure.epic("Authentication")
@allure.feature("Login")
class TestLogin:
    """Tests for the login screen."""

    @pytest.mark.smoke
    @pytest.mark.regression
    @allure.story("Successful Login")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Login with valid credentials")
    @allure.description("Verify that a user with valid credentials can log in and see the home screen.")
    def test_successful_login(self, driver: WebDriver, wiremock: WireMockClient) -> None:
        """A valid user should land on the home screen with a welcome message."""
        with allure.step("Set up WireMock stub for successful login"):
            wiremock.load_mapping_from_file("wiremock/mappings/login_success.json")

        login_page = LoginPage(driver)

        with allure.step(f"Log in as '{VALID_USER.username}'"):
            login_page.login(VALID_USER.username, VALID_USER.password)

        with allure.step("Verify home page is displayed"):
            home_page = HomePage(driver)
            assert home_page.is_home_displayed(), "Home screen did not appear after successful login"

        with allure.step("Verify welcome message contains user name"):
            welcome = home_page.get_welcome_message()
            assert VALID_USER.expected_name in welcome, (
                f"Expected '{VALID_USER.expected_name}' in welcome message, got: '{welcome}'"
            )

    @pytest.mark.smoke
    @pytest.mark.regression
    @allure.story("Failed Login")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Login with invalid credentials")
    @allure.description("Verify that invalid credentials show an error and remain on the login screen.")
    def test_login_invalid_credentials(self, driver: WebDriver, wiremock: WireMockClient) -> None:
        """An invalid user should see an error message and stay on the login screen."""
        with allure.step("Set up WireMock stub for failed login"):
            wiremock.load_mapping_from_file("wiremock/mappings/login_failure.json")

        login_page = LoginPage(driver)

        with allure.step(f"Attempt login as '{INVALID_USER.username}'"):
            login_page.login(INVALID_USER.username, INVALID_USER.password)

        with allure.step("Verify error message is displayed"):
            error_text = login_page.get_error_message()
            assert "Invalid" in error_text or "invalid" in error_text, (
                f"Expected an 'invalid' error message, got: '{error_text}'"
            )

        with allure.step("Verify login button is still visible"):
            assert login_page.is_login_button_displayed(), "Login button should still be visible"

    @pytest.mark.regression
    @allure.story("Input Validation")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Login with empty fields")
    @allure.description("Verify that submitting empty fields triggers a validation error.")
    def test_login_empty_fields(self, driver: WebDriver, wiremock: WireMockClient) -> None:
        """Submitting empty credentials should show a validation error."""
        login_page = LoginPage(driver)

        with allure.step("Tap login with empty credentials"):
            login_page.login("", "")

        with allure.step("Verify validation error is shown"):
            assert login_page.is_login_button_displayed(), "Login button should still be visible"
            error_text = login_page.get_error_message(timeout=5)
            assert error_text, "An error message should be displayed for empty fields"
