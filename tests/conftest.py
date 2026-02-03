"""Pytest configuration — fixtures, hooks, and CLI options."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from src.utils.driver_factory import DriverFactory
from src.utils.wiremock_client import WireMockClient
from src.utils.config_loader import load_settings


# ── CLI Options ───────────────────────────────────────────────────


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--platform",
        action="store",
        default="android",
        choices=["android", "ios"],
        help="Target platform: android or ios",
    )


@pytest.fixture(scope="session")
def platform(request: pytest.FixtureRequest) -> str:
    """Return the target platform from CLI args."""
    return request.config.getoption("--platform")


# ── Driver fixture ────────────────────────────────────────────────


@pytest.fixture(scope="session")
def driver(platform: str):
    """Create an Appium driver for the session, quit when done."""
    _driver = DriverFactory.get_driver(platform)
    yield _driver
    _driver.quit()


# ── WireMock fixture ──────────────────────────────────────────────


@pytest.fixture(scope="session")
def wiremock() -> WireMockClient:
    """Provide a WireMock client for the test session."""
    settings = load_settings()
    base_url = settings["wiremock"]["base_url"]
    client = WireMockClient(base_url)
    return client


@pytest.fixture(autouse=True)
def reset_wiremock(wiremock: WireMockClient) -> None:
    """Reset WireMock stubs before each test for isolation."""
    wiremock.reset()


# ── Screenshot on failure ─────────────────────────────────────────


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call):
    """Capture a screenshot when a test fails."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver:
            screenshot_dir = Path("reports/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            name = item.nodeid.replace("::", "_").replace("/", "_")
            path = screenshot_dir / f"{name}.png"
            driver.save_screenshot(str(path))
