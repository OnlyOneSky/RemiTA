"""User data models for test data."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class User:
    """Test user credentials and expected data."""

    username: str
    password: str
    display_name: str = ""


# ── Pre-defined test users ────────────────────────────────────────

VALID_USER = User(
    username="testuser",
    password="Test@1234",
    display_name="Test User",
)

INVALID_USER = User(
    username="invalid_user",
    password="wrong_password",
    display_name="",
)
