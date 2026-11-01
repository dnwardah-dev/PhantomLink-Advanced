import pytest
from fastapi.testclient import TestClient

from main import app, limiter


@pytest.fixture
def client():
    limiter.reset()
    with TestClient(app) as test_client:
        yield test_client
    limiter.reset()


@pytest.mark.parametrize(
    "origin, expected_status",
    [
        ("http://127.0.0.1:5173", 422),
        ("http://localhost:5173", 422),
        ("https://attacker.example", 403),
        ("http://127.0.0.1:5173.attacker.example", 403),
        ("null", 403),
    ],
)
def test_origin_validation(client, origin, expected_status):
    response = client.post(
        "/api/analyze",
        json={"url": "javascript:alert(1)"},
        headers={"Origin": origin},
    )

    assert response.status_code == expected_status


def test_missing_origin_and_referer_rejected(client):
    response = client.post(
        "/api/analyze",
        json={"url": "javascript:alert(1)"},
    )

    assert response.status_code == 403


def test_trusted_referer_accepted(client):
    response = client.post(
        "/api/analyze",
        json={"url": "javascript:alert(1)"},
        headers={
            "Referer": "http://127.0.0.1:5173/investigate"
        },
    )

    assert response.status_code == 422


def test_untrusted_referer_rejected(client):
    response = client.post(
        "/api/analyze",
        json={"url": "javascript:alert(1)"},
        headers={
            "Referer": "https://attacker.example/fake"
        },
    )

    assert response.status_code == 403
