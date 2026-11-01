"""Security header regression tests."""

from fastapi.testclient import TestClient

from main import app
from app.services.security_headers import apply_security_headers
from starlette.responses import Response


def test_api_security_headers():
    with TestClient(app) as client:
        for endpoint in ["/", "/health"]:
            response = client.get(endpoint)

            assert response.status_code == 200
            assert response.headers["x-content-type-options"] == "nosniff"
            assert response.headers["x-frame-options"] == "DENY"
            assert response.headers["referrer-policy"] == "no-referrer"

            assert (
                "frame-ancestors 'none'"
                in response.headers["content-security-policy"]
            )

            assert (
                "camera=()"
                in response.headers["permissions-policy"]
            )


def test_development_does_not_enable_hsts():
    response = Response()

    apply_security_headers(
        response,
        environment="development",
    )

    assert "strict-transport-security" not in response.headers


def test_production_enables_hsts():
    response = Response()

    apply_security_headers(
        response,
        environment="production",
    )

    assert (
        response.headers["strict-transport-security"]
        == "max-age=31536000"
    )
