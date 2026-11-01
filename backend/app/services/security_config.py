"""Centralized environment-based security configuration."""

import os


class SecurityConfigurationError(RuntimeError):
    """Raised when security configuration is unsafe or invalid."""


def get_cookie_security_config(
    environment: str | None = None,
    secure_setting: str | None = None,
) -> dict:
    if environment is None:
        environment = os.getenv("PHANTOMLINK_ENV", "development")

    if secure_setting is None:
        secure_setting = os.getenv(
            "PHANTOMLINK_COOKIE_SECURE", "false"
        )

    environment = environment.strip().lower()
    secure_setting = secure_setting.strip().lower()

    if environment not in {"development", "test", "production"}:
        raise SecurityConfigurationError(
            "PHANTOMLINK_ENV must be development, test, or production."
        )

    if secure_setting not in {"true", "false"}:
        raise SecurityConfigurationError(
            "PHANTOMLINK_COOKIE_SECURE must be true or false."
        )

    secure = secure_setting == "true"

    if environment == "production" and not secure:
        raise SecurityConfigurationError(
            "Production requires Secure session cookies. "
            "Set PHANTOMLINK_COOKIE_SECURE=true."
        )

    return {
        "environment": environment,
        "cookie_secure": secure,
        "cookie_httponly": True,
        "cookie_samesite": "lax",
        "cookie_path": "/",
    }
