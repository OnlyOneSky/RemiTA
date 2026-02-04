"""AppInstaller — check if the app is installed on a device and install if needed."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from src.models.device_info import DeviceInfo

logger = logging.getLogger(__name__)


class AppInstaller:
    """Ensures the target app is installed on a device before testing."""

    # ── Public API ────────────────────────────────────────────────

    @classmethod
    def ensure_installed(
        cls,
        device: DeviceInfo,
        app_package: str,
        app_path: str | None = None,
    ) -> bool:
        """Check if the app is installed; install it if not.

        Parameters
        ----------
        device:
            The target device.
        app_package:
            Package name (Android) or bundle ID (iOS) to check.
        app_path:
            Path to the APK/IPA file for installation.

        Returns
        -------
        bool
            ``True`` if the app is (now) installed, ``False`` on failure.
        """
        if device.platform == "android":
            return cls._ensure_android(device, app_package, app_path)
        elif device.platform == "ios":
            return cls._ensure_ios(device, app_package, app_path)
        else:
            logger.error("Unsupported platform: %s", device.platform)
            return False

    @classmethod
    def is_installed(cls, device: DeviceInfo, app_package: str) -> bool:
        """Check if the app is installed without attempting to install."""
        if device.platform == "android":
            return cls._is_installed_android(device.serial, app_package)
        elif device.platform == "ios":
            return cls._is_installed_ios(device.serial, app_package, device.is_emulator)
        return False

    # ── Android ───────────────────────────────────────────────────

    @classmethod
    def _is_installed_android(cls, serial: str, package: str) -> bool:
        """Check if an Android package is installed via ``adb``."""
        try:
            result = subprocess.run(
                ["adb", "-s", serial, "shell", "pm", "list", "packages", package],
                capture_output=True, text=True, timeout=15,
            )
            # pm list packages returns lines like "package:com.remita.sample"
            installed = f"package:{package}" in result.stdout
            logger.info(
                "App %s on %s: %s",
                package, serial, "INSTALLED" if installed else "NOT INSTALLED",
            )
            return installed
        except Exception:
            logger.warning("Failed to check app installation on %s", serial, exc_info=True)
            return False

    @classmethod
    def _install_android(cls, serial: str, apk_path: str) -> bool:
        """Install an APK on an Android device via ``adb``."""
        path = Path(apk_path)
        if not path.exists():
            logger.error("APK not found: %s", apk_path)
            return False

        logger.info("Installing APK on %s: %s", serial, apk_path)
        try:
            result = subprocess.run(
                ["adb", "-s", serial, "install", "-r", str(path)],
                capture_output=True, text=True, timeout=120,
            )
            if "Success" in result.stdout:
                logger.info("APK installed successfully on %s", serial)
                return True
            else:
                logger.error(
                    "APK install failed on %s: %s %s",
                    serial, result.stdout.strip(), result.stderr.strip(),
                )
                return False
        except subprocess.TimeoutExpired:
            logger.error("APK install timed out on %s", serial)
            return False
        except Exception:
            logger.error("APK install failed on %s", serial, exc_info=True)
            return False

    @classmethod
    def _ensure_android(
        cls, device: DeviceInfo, package: str, apk_path: str | None
    ) -> bool:
        if not apk_path:
            if cls._is_installed_android(device.serial, package):
                logger.info("✅ %s already installed on %s — no APK path, skipping", package, device.display_name)
                return True
            logger.error(
                "❌ %s not installed on %s and no APK path provided",
                package, device.display_name,
            )
            return False

        # Always reinstall when APK path is provided to ensure latest version
        if cls._is_installed_android(device.serial, package):
            logger.info("🔄 %s found on %s — reinstalling with latest APK", package, device.display_name)
        else:
            logger.info("📦 %s not found on %s — installing", package, device.display_name)

        return cls._install_android(device.serial, apk_path)

    # ── iOS ───────────────────────────────────────────────────────

    @classmethod
    def _is_installed_ios(cls, udid: str, bundle_id: str, is_simulator: bool) -> bool:
        """Check if an iOS app is installed."""
        try:
            if is_simulator:
                result = subprocess.run(
                    ["xcrun", "simctl", "listapps", udid],
                    capture_output=True, text=True, timeout=15,
                )
                return bundle_id in result.stdout
            else:
                # For real devices, use ideviceinstaller or ios-deploy
                result = subprocess.run(
                    ["ideviceinstaller", "-u", udid, "-l"],
                    capture_output=True, text=True, timeout=15,
                )
                return bundle_id in result.stdout
        except Exception:
            logger.warning("Failed to check iOS app on %s", udid, exc_info=True)
            return False

    @classmethod
    def _install_ios(cls, udid: str, app_path: str, is_simulator: bool) -> bool:
        """Install an app on an iOS device or simulator."""
        path = Path(app_path)
        if not path.exists():
            logger.error("App not found: %s", app_path)
            return False

        try:
            if is_simulator:
                result = subprocess.run(
                    ["xcrun", "simctl", "install", udid, str(path)],
                    capture_output=True, text=True, timeout=60,
                )
            else:
                result = subprocess.run(
                    ["ideviceinstaller", "-u", udid, "-i", str(path)],
                    capture_output=True, text=True, timeout=120,
                )

            if result.returncode == 0:
                logger.info("App installed successfully on %s", udid)
                return True
            else:
                logger.error("App install failed: %s", result.stderr.strip())
                return False
        except Exception:
            logger.error("App install failed on %s", udid, exc_info=True)
            return False

    @classmethod
    def _ensure_ios(
        cls, device: DeviceInfo, bundle_id: str, app_path: str | None
    ) -> bool:
        if cls._is_installed_ios(device.serial, bundle_id, device.is_emulator):
            logger.info("✅ %s already installed on %s — skipping install", bundle_id, device.display_name)
            return True

        if not app_path:
            logger.error(
                "❌ %s not installed on %s and no app path provided",
                bundle_id, device.display_name,
            )
            return False

        logger.info("📦 Installing %s on %s...", bundle_id, device.display_name)
        return cls._install_ios(device.serial, app_path, device.is_emulator)
