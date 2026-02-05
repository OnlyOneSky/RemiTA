"""WireMockClient — programmatic control of a WireMock instance."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)


class WireMockClient:
    """Thin REST client for WireMock's ``__admin`` API.

    Usage::

        wm = WireMockClient("http://localhost:8080")
        wm.create_stub({
            "request": {"method": "GET", "url": "/api/health"},
            "response": {"status": 200, "jsonBody": {"ok": True}},
        })
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self._admin = f"{self.base_url}/__admin"

    # ── Health ────────────────────────────────────────────────────────────

    def is_healthy(self, timeout: float = 5.0) -> bool:
        """Return ``True`` if WireMock is reachable."""
        try:
            resp = requests.get(f"{self._admin}/mappings", timeout=timeout)
            return resp.status_code == 200
        except requests.ConnectionError:
            return False

    # ── Stub management ───────────────────────────────────────────────────

    def create_stub(self, mapping: dict[str, Any]) -> dict[str, Any]:
        """Create a new stub mapping and return the WireMock response."""
        resp = requests.post(
            f"{self._admin}/mappings",
            json=mapping,
            timeout=10,
        )
        resp.raise_for_status()
        logger.debug("Stub created: %s", resp.json())
        return resp.json()

    def load_mapping_from_file(self, file_path: str | Path) -> dict[str, Any]:
        """Read a JSON mapping file and register it as a stub."""
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as fh:
            mapping: dict[str, Any] = json.load(fh)
        return self.create_stub(mapping)

    def load_mappings_from_dir(self, dir_path: str | Path, pattern: str = "*.json") -> int:
        """Load all mapping files matching *pattern* from a directory.

        Returns the number of mappings loaded.
        """
        directory = Path(dir_path)
        count = 0
        for file in sorted(directory.glob(pattern)):
            try:
                self.load_mapping_from_file(file)
                count += 1
            except Exception:
                logger.warning("Failed to load mapping: %s", file, exc_info=True)
        logger.info("Loaded %d mapping(s) from %s", count, directory)
        return count

    def delete_all_stubs(self) -> None:
        """Remove every stub mapping."""
        resp = requests.delete(f"{self._admin}/mappings", timeout=10)
        resp.raise_for_status()
        logger.info("All stubs deleted.")

    def reset(self) -> None:
        """Reset all stubs **and** the request journal."""
        resp = requests.post(f"{self._admin}/reset", timeout=10)
        resp.raise_for_status()
        logger.info("WireMock reset.")

    # ── Request verification ──────────────────────────────────────────────

    def verify_request(
        self,
        url: str,
        method: str = "GET",
        expected_count: int | None = None,
    ) -> dict[str, Any]:
        """Query the request journal and optionally assert the call count.

        Parameters
        ----------
        url:
            The URL path to verify (e.g., ``"/api/login"``).
        method:
            HTTP method (``GET``, ``POST``, etc.).
        expected_count:
            If provided, an ``AssertionError`` is raised when the actual
            count does not match.

        Returns
        -------
        dict
            The raw verification response from WireMock.
        """
        payload = {
            "method": method.upper(),
            "url": url,
        }
        resp = requests.post(
            f"{self._admin}/requests/count",
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()

        if expected_count is not None:
            actual = data.get("count", 0)
            assert actual == expected_count, (
                f"Expected {expected_count} request(s) to {method} {url}, got {actual}"
            )

        return data
