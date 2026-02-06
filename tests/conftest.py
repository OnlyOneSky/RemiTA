"""Pytest configuration — fixtures, hooks, and CLI options."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Generator, List
from urllib.parse import urlparse

import allure
import pytest
from _pytest.config.argparsing import Parser
from _pytest.nodes import Item
from _pytest.python import Metafunc

from src.models.device_info import DeviceInfo
from src.utils.app_installer import AppInstaller
from src.utils.config_loader import ConfigLoader
from src.utils.device_manager import DeviceManager
from src.utils.driver_factory import DriverFactory
from src.utils.wiremock_client import WireMockClient

logger = logging.getLogger(__name__)

ALLURE_RESULTS_DIR = Path("allure-results")
ALLURE_CONFIG_DIR = Path("allure-config")


# ── CLI options ───────────────────────────────────────────────────────────────


def pytest_addoption(parser: Parser) -> None:
    """Register custom command-line options."""
    parser.addoption(
        "--platform",
        action="store",
        default="all",
        choices=["android", "ios", "all"],
        help="Target platform: android, ios, or all (default: all)",
    )


# ── Device discovery ──────────────────────────────────────────────────────────


def _discover_devices(platform: str) -> List[DeviceInfo]:
    """Discover devices based on the --platform flag."""
    if platform == "android":
        devices = DeviceManager.discover_android()
    elif platform == "ios":
        devices = DeviceManager.discover_ios()
    else:  # "all"
        devices = DeviceManager.discover_all()

    if not devices:
        pytest.exit(
            f"No devices found for platform='{platform}'. "
            "Connect a device or start an emulator/simulator, then retry.",
            returncode=1,
        )

    logger.info(
        "Running regression on %d device(s): %s",
        len(devices),
        ", ".join(d.display_name for d in devices),
    )
    return devices


# Cache discovered devices for the session (avoid re-running adb/xcrun per test)
_cached_devices: List[DeviceInfo] | None = None


def _get_devices(platform: str) -> List[DeviceInfo]:
    global _cached_devices
    if _cached_devices is None:
        _cached_devices = _discover_devices(platform)
    return _cached_devices


# ── Dynamic parametrization ───────────────────────────────────────────────────


def pytest_generate_tests(metafunc: Metafunc) -> None:
    """Parametrize tests that use the ``device_info`` fixture.

    Every test that requests ``device_info`` will be run once per
    discovered device. Tests that don't request it run normally.
    """
    if "device_info" in metafunc.fixturenames:
        platform = metafunc.config.getoption("--platform")
        devices = _get_devices(platform)
        metafunc.parametrize(
            "device_info",
            devices,
            ids=[d.allure_label for d in devices],
            scope="session",
        )


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def platform(request: pytest.FixtureRequest) -> str:
    """Return the selected platform from CLI args."""
    return request.config.getoption("--platform")  # type: ignore[return-value]


@pytest.fixture(scope="session")
def driver(device_info: DeviceInfo) -> Generator:
    """Create an Appium driver for a specific device, quit it afterwards.

    Before creating the driver, checks if the app is installed on the device.
    If not, installs it automatically from the configured APK/IPA path.

    This fixture is parametrized indirectly via ``device_info``.
    Each device gets its own driver instance.
    """
    # ── Ensure app is installed before creating driver ──
    config = ConfigLoader.load_merged_config(device_info.platform)
    caps = config.get("capabilities", {})
    app_package = caps.get("appium:appPackage") or caps.get("appium:bundleId", "")
    app_path_raw = caps.get("appium:app")
    app_path = str(ConfigLoader.resolve_path(app_path_raw)) if app_path_raw else None

    if app_package:
        installed = AppInstaller.ensure_installed(device_info, app_package, app_path)
        if not installed:
            pytest.fail(
                f"App '{app_package}' could not be installed on {device_info.display_name}. "
                f"Check that the APK/IPA exists at: {app_path}"
            )

    _driver = DriverFactory.get_driver_for_device(device_info)
    logger.info(
        "Driver ready for %s (session=%s)",
        device_info.display_name, _driver.session_id,
    )

    # Tag the Allure report with device info
    allure.dynamic.parameter("device", device_info.display_name)
    allure.dynamic.label("device", device_info.allure_label)

    yield _driver

    logger.info("Quitting driver for %s", device_info.display_name)
    _driver.quit()


@pytest.fixture(scope="session")
def wiremock() -> Generator[WireMockClient, None, None]:
    """Provide a ``WireMockClient`` for the session."""
    settings = ConfigLoader.load_settings()
    base_url: str = settings.get("wiremock", {}).get("base_url", "http://localhost:8080")
    client = WireMockClient(base_url)
    logger.info("WireMockClient connected → %s (healthy=%s)", base_url, client.is_healthy())
    yield client


@pytest.fixture(scope="session", autouse=True)
def _setup_adb_reverse(device_info: DeviceInfo, driver) -> Generator[None, None, None]:
    """Set up adb reverse port forwarding after Appium driver is created.

    Appium's UiAutomator2 driver may restart the ADB server during session
    initialization, which clears any manually configured ``adb reverse``
    mappings.  This fixture re-establishes port forwarding so the emulator
    app can reach WireMock on the host.
    """
    if device_info.platform == "android":
        settings = ConfigLoader.load_settings()
        wiremock_url = settings.get("wiremock", {}).get("base_url", "http://localhost:8080")
        port = urlparse(wiremock_url).port or 8080

        try:
            result = subprocess.run(
                ["adb", "-s", device_info.serial, "reverse", f"tcp:{port}", f"tcp:{port}"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                logger.info("✅ adb reverse tcp:%s → tcp:%s on %s", port, port, device_info.serial)
            else:
                logger.warning("⚠️ adb reverse failed: %s", result.stderr.strip())
        except Exception:
            logger.warning("⚠️ Could not set up adb reverse", exc_info=True)

    yield


@pytest.fixture(autouse=True)
def _reset_app_state(driver) -> Generator[None, None, None]:
    """Reset the app to a clean state before each test.

    Restarts the app and waits for splash + init API calls to complete.
    Dialog dismissal is handled by each test's page objects since
    different flows may need different handling.
    """
    # Force implicit wait to 0 for faster element lookups
    driver.implicitly_wait(0)
    
    driver.terminate_app(driver.capabilities.get("appPackage", ""))
    driver.activate_app(driver.capabilities.get("appPackage", ""))
    import time
    time.sleep(3)  # Wait for splash + init API calls to complete
    yield


# Path to the WireMock mappings directory (relative to project root).
_WIREMOCK_MAPPINGS_DIR = Path("wiremock/mappings")


def _load_init_stubs(client: WireMockClient) -> None:
    """Reload the app init stubs and catch-all that WireMock needs.

    These stubs are required for the app to survive its splash-screen
    startup API calls (public key, customer service, etc.).
    """
    for f in sorted(_WIREMOCK_MAPPINGS_DIR.glob("app_*.json")):
        try:
            client.load_mapping_from_file(f)
        except Exception:
            logger.warning("Failed to load init stub: %s", f, exc_info=True)


@pytest.fixture(autouse=True)
def _reset_wiremock(wiremock: WireMockClient) -> Generator[None, None, None]:
    """Auto-use fixture that resets WireMock stubs before and after every test.

    Before: Reset and load init stubs so app startup API calls work.
    After: Reset and reload for the next test.
    """
    # BEFORE test: ensure init stubs are loaded
    try:
        wiremock.reset()
        _load_init_stubs(wiremock)
    except Exception:
        logger.warning("Failed to setup WireMock before test", exc_info=True)
    
    yield
    
    # AFTER test: reset for clean state (next test will reload)
    try:
        wiremock.reset()
        _load_init_stubs(wiremock)
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


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Copy Allure environment and categories config into results dir."""
    if not ALLURE_RESULTS_DIR.exists():
        return

    for filename in ("environment.properties", "categories.json"):
        src = ALLURE_CONFIG_DIR / filename
        if src.exists():
            shutil.copy(str(src), str(ALLURE_RESULTS_DIR / filename))
