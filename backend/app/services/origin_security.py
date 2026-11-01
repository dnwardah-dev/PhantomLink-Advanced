
"""Origin verification for browser state-changing requests."""

import os
from urllib.parse import urlsplit


def get_allowed_origins() -> set[str]:
    configured = os.getenv(
        "PHANTOMLINK_ALLOWED_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173",
    )

    return {
        value.strip().rstrip("/")
        for value in configured.split(",")
        if value.strip()
    }


def is_trusted_origin(origin: str | None) -> bool:
    if not origin or origin == "null":
        return False

    try:
        parsed = urlsplit(origin)

        if (
            parsed.scheme not in ("http", "https")
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path not in ("", "/")
            or parsed.query
            or parsed.fragment
        ):
            return False

        normalized = (
            f"{parsed.scheme}://{parsed.hostname}"
            + (f":{parsed.port}" if parsed.port else "")
        )
    except ValueError:
        return False

    return normalized in get_allowed_origins()


def is_allowed_browser_request(
    origin: str | None,
    referer: str | None = None,
) -> bool:
    if origin is not None:
        return is_trusted_origin(origin)

    if not referer:
        return False

    try:
        parsed = urlsplit(referer)
        if not parsed.scheme or not parsed.netloc:
            return False
        referer_origin = (
            f"{parsed.scheme}://{parsed.hostname}"
            + (f":{parsed.port}" if parsed.port else "")
        )
    except ValueError:
        return False

    return is_trusted_origin(referer_origin)
