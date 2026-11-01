"""HTTP integration tests for PhantomLink V2."""

import pytest
from fastapi.testclient import TestClient

from main import app


ALLOWED_ORIGIN = "http://127.0.0.1:5173"
BLOCKED_ORIGIN = "https://untrusted.example"


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def post_v2(client, url, origin=ALLOWED_ORIGIN):
    return client.post(
        "/api/investigate/v2",
        json={"url": url},
        headers={"Origin": origin},
    )


def test_valid_url_returns_experimental_result(client):
    response = post_v2(client, "https://example.com/")

    assert response.status_code == 200

    data = response.json()

    assert data["engine"] == "PHANTOMLINK_V2_PIPELINE"
    assert data["status"] == "analyzed"
    assert data["hostname"] == "example.com"
    assert data["network_requests_performed"] is False
    assert data["is_phishing_verdict"] is False
    assert data["interpretation"]["is_probability"] is False


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost/admin",
        "http://127.0.0.1/",
        "http://192.168.1.1/",
        "http://169.254.169.254/",
        "https://foo..example.com/",
        "https://foo_bar.example.com/",
        "https://" + "a" * 64 + ".example.com/",
        "https://user@example.com/",
    ],
)
def test_invalid_urls_rejected(client, url):
    response = post_v2(client, url)
    assert response.status_code == 400


def test_untrusted_origin_rejected(client):
    response = post_v2(
        client,
        "https://example.com/",
        origin=BLOCKED_ORIGIN,
    )

    assert response.status_code == 403


def test_missing_origin_rejected(client):
    response = client.post(
        "/api/investigate/v2",
        json={"url": "https://example.com/"},
    )

    assert response.status_code == 403


def test_unicode_hostname_canonicalized(client):
    response = post_v2(
        client,
        "https://b\u00fccher.example/login",
    )

    assert response.status_code == 200
    assert response.json()["hostname"] == "xn--bcher-kva.example"


def test_legacy_investigation_route_preserved():
    assert any(
        getattr(route, "path", None) == "/api/investigate"
        for route in app.routes
    )
