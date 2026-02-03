"""WireMock REST client — manage stubs programmatically during tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests


class WireMockClient:
    """Thin wrapper around the WireMock Admin API."""

    def __init__(self, base_url: str = "http://127.0.0.1:8080") -> None:
        self.base_url = base_url.rstrip("/")
        self.admin_url = f"{self.base_url}/__admin"

    # ── Health ────────────────────────────────────────────────────

    def is_healthy(self) -> bool:
        """Check if WireMock is up and responding."""
        try:
            resp = requests.get(f"{self.admin_url}/mappings", timeout=5)
            return resp.status_code == 200
        except requests.ConnectionError:
            return False

    # ── Stub management ───────────────────────────────────────────

    def create_stub(self, mapping: dict[str, Any]) -> dict[str, Any]:
        """Create a new stub mapping.

        Args:
            mapping: WireMock mapping dict with 'request' and 'response' keys.

        Returns:
            Created mapping response from WireMock.
        """
        resp = requests.post(
            f"{self.admin_url}/mappings",
            json=mapping,
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    def load_mapping_from_file(self, file_path: str | Path) -> dict[str, Any]:
        """Load a mapping JSON file and create the stub.

        Args:
            file_path: Path to the mapping JSON file.

        Returns:
            Created mapping response from WireMock.
        """
        with open(file_path, "r") as f:
            mapping = json.load(f)
        return self.create_stub(mapping)

    def delete_all_stubs(self) -> None:
        """Remove all stub mappings."""
        resp = requests.delete(f"{self.admin_url}/mappings")
        resp.raise_for_status()

    def reset(self) -> None:
        """Reset WireMock — clears stubs, request journal, and scenarios."""
        resp = requests.post(f"{self.admin_url}/reset")
        resp.raise_for_status()

    # ── Verification ──────────────────────────────────────────────

    def verify_request(
        self, url: str, method: str = "POST", expected_count: int | None = None
    ) -> dict[str, Any]:
        """Verify that a specific request was received.

        Args:
            url: The request URL path to verify.
            method: HTTP method (default POST).
            expected_count: If set, assert exactly this many matching requests.

        Returns:
            Verification response with request details.
        """
        payload: dict[str, Any] = {
            "method": method,
            "url": url,
        }

        if expected_count is not None:
            resp = requests.post(
                f"{self.admin_url}/requests/count",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            actual = data.get("count", 0)
            assert actual == expected_count, (
                f"Expected {expected_count} request(s) to {method} {url}, got {actual}"
            )
            return data

        resp = requests.post(
            f"{self.admin_url}/requests/find",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()

    def get_request_journal(self) -> list[dict[str, Any]]:
        """Return all recorded requests."""
        resp = requests.get(f"{self.admin_url}/requests")
        resp.raise_for_status()
        return resp.json().get("requests", [])
