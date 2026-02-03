"""Device discovery — find connected Android and iOS devices."""

from __future__ import annotations

import logging
import re
import subprocess
from typing import List

from src.models.device_info import DeviceInfo

logger = logging.getLogger(__name__)


class DeviceManager:
    """Discover real devices, emulators, and simulators."""

    # ── Public API ────────────────────────────────────────────────

    @classmethod
    def discover_all(cls) -> List[DeviceInfo]:
        """Return all connected Android + iOS devices."""
        devices: List[DeviceInfo] = []
        devices.extend(cls.discover_android())
        devices.extend(cls.discover_ios())
        logger.info("Discovered %d device(s) total", len(devices))
        return devices

    @classmethod
    def discover_android(cls) -> List[DeviceInfo]:
        """Discover connected Android devices and emulators via ``adb``."""
        devices: List[DeviceInfo] = []

        try:
            result = subprocess.run(
                ["adb", "devices", "-l"],
                capture_output=True, text=True, timeout=15,
            )
        except FileNotFoundError:
            logger.warning("adb not found — skipping Android device discovery")
            return devices
        except subprocess.TimeoutExpired:
            logger.warning("adb devices timed out")
            return devices

        for line in result.stdout.strip().splitlines()[1:]:  # skip header
            line = line.strip()
            if not line or "offline" in line:
                continue

            parts = line.split()
            serial = parts[0]
            # status is parts[1] (should be "device")
            if len(parts) < 2 or parts[1] != "device":
                continue

            # Parse key:value pairs from the rest of the line
            props = {}
            for part in parts[2:]:
                if ":" in part:
                    k, v = part.split(":", 1)
                    props[k] = v

            device = DeviceInfo(
                serial=serial,
                platform="android",
                device_name=props.get("model", "").replace("_", " "),
                model=props.get("model", ""),
                is_emulator=serial.startswith("emulator-") or "sdk" in props.get("model", "").lower(),
            )

            # Fetch extra properties from the device
            device.platform_version = cls._adb_getprop(serial, "ro.build.version.release")
            device.manufacturer = cls._adb_getprop(serial, "ro.product.manufacturer")

            if not device.device_name:
                device.device_name = cls._adb_getprop(serial, "ro.product.model")

            logger.info("Found Android device: %s", device.display_name)
            devices.append(device)

        return devices

    @classmethod
    def discover_ios(cls) -> List[DeviceInfo]:
        """Discover connected iOS devices and simulators via ``xcrun``."""
        devices: List[DeviceInfo] = []

        # ── Real devices via xcrun xctrace ──
        devices.extend(cls._discover_ios_real_devices())

        # ── Booted simulators via xcrun simctl ──
        devices.extend(cls._discover_ios_simulators())

        return devices

    # ── Android helpers ───────────────────────────────────────────

    @classmethod
    def _adb_getprop(cls, serial: str, prop: str) -> str:
        """Read a single system property from an Android device."""
        try:
            result = subprocess.run(
                ["adb", "-s", serial, "shell", "getprop", prop],
                capture_output=True, text=True, timeout=10,
            )
            return result.stdout.strip()
        except Exception:
            return ""

    # ── iOS helpers ───────────────────────────────────────────────

    @classmethod
    def _discover_ios_real_devices(cls) -> List[DeviceInfo]:
        """Find physical iOS devices via ``xcrun xctrace list devices``."""
        devices: List[DeviceInfo] = []

        try:
            result = subprocess.run(
                ["xcrun", "xctrace", "list", "devices"],
                capture_output=True, text=True, timeout=15,
            )
        except FileNotFoundError:
            logger.warning("xcrun not found — skipping iOS device discovery")
            return devices
        except subprocess.TimeoutExpired:
            logger.warning("xcrun xctrace timed out")
            return devices

        # Output format: "Device Name (version) (udid)"
        # Skip lines until we see "== Devices ==" header
        in_devices_section = False
        in_simulators_section = False

        for line in result.stdout.splitlines():
            line = line.strip()

            if "== Devices ==" in line:
                in_devices_section = True
                in_simulators_section = False
                continue
            if "== Simulators ==" in line:
                in_devices_section = False
                in_simulators_section = True
                continue

            if not in_devices_section or not line:
                continue

            # Skip the host Mac line
            match = re.match(r"^(.+?)\s+\((\d+[\d.]*)\)\s+\(([A-Fa-f0-9-]+)\)$", line)
            if match:
                name, version, udid = match.groups()
                device = DeviceInfo(
                    serial=udid,
                    platform="ios",
                    device_name=name.strip(),
                    platform_version=version,
                    is_emulator=False,
                    manufacturer="Apple",
                )
                logger.info("Found iOS device: %s", device.display_name)
                devices.append(device)

        return devices

    @classmethod
    def _discover_ios_simulators(cls) -> List[DeviceInfo]:
        """Find booted iOS simulators via ``xcrun simctl list``."""
        devices: List[DeviceInfo] = []

        try:
            result = subprocess.run(
                ["xcrun", "simctl", "list", "devices", "booted"],
                capture_output=True, text=True, timeout=15,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return devices

        # Output: "-- iOS 17.4 --" then "    iPhone 15 (UDID) (Booted)"
        current_version = ""

        for line in result.stdout.splitlines():
            line = line.strip()

            version_match = re.match(r"^-- iOS ([\d.]+) --$", line)
            if version_match:
                current_version = version_match.group(1)
                continue

            device_match = re.match(r"^(.+?)\s+\(([A-Fa-f0-9-]+)\)\s+\(Booted\)$", line)
            if device_match:
                name, udid = device_match.groups()
                device = DeviceInfo(
                    serial=udid,
                    platform="ios",
                    device_name=name.strip(),
                    platform_version=current_version,
                    is_emulator=True,
                    manufacturer="Apple",
                )
                logger.info("Found iOS simulator: %s", device.display_name)
                devices.append(device)

        return devices
