"""Device information model — represents a connected physical or virtual device."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DeviceInfo:
    """Holds all metadata about a discovered device."""

    serial: str                         # adb serial or iOS UDID
    platform: str                       # "android" or "ios"
    device_name: str = ""               # "Pixel 7", "iPhone 15", etc.
    platform_version: str = ""          # "14", "17.4", etc.
    is_emulator: bool = False           # True for emulators / simulators
    model: str = ""                     # Hardware model (e.g. "sdk_gphone64_arm64")
    manufacturer: str = ""              # "Google", "Apple", etc.
    extra: dict = field(default_factory=dict)  # Any additional properties

    @property
    def display_name(self) -> str:
        """Human-friendly label for reports and logs."""
        emu_tag = " (emulator)" if self.is_emulator else ""
        version = f" {self.platform_version}" if self.platform_version else ""
        name = self.device_name or self.model or self.serial
        return f"{name}{version}{emu_tag}"

    @property
    def allure_label(self) -> str:
        """Short label for Allure parameterization."""
        name = self.device_name or self.model or self.serial
        return name.replace(" ", "_")
