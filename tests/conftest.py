"""Pytest configuration — fixtures, hooks, and CLI options."""

from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from typing import Generator

import allure
import pytest
from _pytest.config.argparsing import Parser
from _pytest.nodes import Item

from src.utils.config_loader import ConfigLoader
from src.utils.driver_factory import DriverFactory
from src.utils.wiremock_client import WireMockClient

ALLURE_RESULTS_DIR = Path("allure-results")
ALLURE_CONFIG_DIR = Path("allure-config")

logger = logging.getLogger(__name__)


# ── CLI options ───────────────────────────────────────────────────────────────


def pytest_addoption(parser: Parser) -> None:
    """Register custom command-line options."""
    parser.addoption(
        "--platform",
        action="store",
        default="android",
        choices=["android", "ios"],
        help="Target platform: android (default) or ios",
    )


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def platform(request: pytest.FixtureRequest) -> str:
    """Return the selected platform (``android`` or ``ios``)."""
    return request.config.getoption("--platform")  # type: ignore[return-value]


@pytest.fixture(scope="session")
def driver(platform: str) -> Generator:
    """Create an Appium driver for the session, quit it afterwards."""
    _driver = DriverFactory.get_driver(platform)
    logger.info("Appium driver created for platform=%s (session=%s)", platform, _driver.session_id)
    yield _driver
    logger.info("Quitting Appium driver (session=%s)", _driver.session_id)
    _driver.quit()


@pytest.fixture(scope="session")
def wiremock() -> Generator[WireMockClient, None, None]:
    """Provide a ``WireMockClient`` for the session.

    Stubs are reset **after each test** via the ``autouse`` fixture below so
    tests remain isolated.
    """
    settings = ConfigLoader.load_settings()
    base_url: str = settings.get("wiremock", {}).get("base_url", "http://localhost:8080")
    client = WireMockClient(base_url)
    logger.info("WireMockClient connected → %s (healthy=%s)", base_url, client.is_healthy())
    yield client


@pytest.fixture(autouse=True)
def _reset_wiremock(wiremock: WireMockClient) -> Generator[None, None, None]:
    """Auto-use fixture that resets WireMock stubs after every test."""
    yield
    try:
        wiremock.reset()
    except Exception:
        logger.warning("Failed to reset WireMock after test", exc_info=True)


# ── Hooks ─────────────────────────────────────────────────────────────────────


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: Item) -> Generator:  # type: ignore[type-arg]
    """Take a screenshot on test failure and attach it to Allure report."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        settings = ConfigLoader.load_settings()
        if not settings.get("screenshots", {}).get("on_failure", True):
            return

        driver = item.funcargs.get("driver")
        if driver is None:
            return

        screenshot_dir = settings.get("screenshots", {}).get("output_dir", "reports/screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)

        file_name = f"{item.nodeid.replace('::', '_').replace('/', '_')}.png"
        file_path = os.path.join(screenshot_dir, file_name)

        try:
            driver.save_screenshot(file_path)
            logger.info("Screenshot saved → %s", file_path)

            # Attach screenshot to Allure report
            with open(file_path, "rb") as f:
                allure.attach(
                    f.read(),
                    name=f"failure_{file_name}",
                    attachment_type=allure.attachment_type.PNG,
                )
        except Exception:
            logger.warning("Failed to take screenshot for %s", item.nodeid, exc_info=True)


# ── Allure environment setup ─────────────────────────────────────────────────


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Copy Allure environment and categories config into results dir."""
    if not ALLURE_RESULTS_DIR.exists():
        return

    for filename in ("environment.properties", "categories.json"):
        src = ALLURE_CONFIG_DIR / filename
        if src.exists():
            shutil.copy(str(src), str(ALLURE_RESULTS_DIR / filename))
