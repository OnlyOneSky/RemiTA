"""Login feature tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.models.user import VALID_USER, INVALID_USER
from src.pages.login_page import LoginPage
from src.pages.home_page import HomePage

MAPPINGS_DIR = Path(__file__).resolve().parents[1] / "wiremock" / "mappings"


@pytest.mark.smoke
@pytest.mark.login
class TestLogin:
    """Login screen test cases."""

    def test_successful_login(self, driver, wiremock) -> None:
        """Valid credentials should navigate to the home page."""
        # Arrange — load WireMock stub for successful login
        wiremock.load_mapping_from_file(MAPPINGS_DIR / "login_success.json")

        login_page = LoginPage(driver)
        home_page = HomePage(driver)

        # Act
        login_page.login(VALID_USER.username, VALID_USER.password)

        # Assert
        assert home_page.is_home_displayed(), "Home page should be visible after login"
        assert VALID_USER.display_name in home_page.get_welcome_message()

        # Verify the API was called
        wiremock.verify_request("/api/login", method="POST", expected_count=1)

    def test_login_invalid_credentials(self, driver, wiremock) -> None:
        """Invalid credentials should show an error message."""
        # Arrange
        wiremock.load_mapping_from_file(MAPPINGS_DIR / "login_failure.json")

        login_page = LoginPage(driver)

        # Act
        login_page.login(INVALID_USER.username, INVALID_USER.password)

        # Assert
        error = login_page.get_error_message()
        assert "Invalid" in error or "invalid" in error, f"Expected error message, got: {error}"

    @pytest.mark.regression
    def test_login_empty_fields(self, driver, wiremock) -> None:
        """Submitting empty fields should show validation error."""
        login_page = LoginPage(driver)

        # Act — tap login without entering anything
        login_page.tap_login()

        # Assert — should remain on login page with an error
        assert login_page.is_login_button_displayed(), "Should stay on login page"
