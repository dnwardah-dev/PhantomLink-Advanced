"""Rate limiting and session behavior tests for V2."""

import uuid

from fastapi.testclient import TestClient

from main import app


ALLOWED_ORIGIN = "http://127.0.0.1:5173"


def test_v2_rate_limit():
    # A unique TestClient address gives this test its own rate-limit key.
    unique_ip = f"198.51.100.{uuid.uuid4().int % 200 + 1}"

    with TestClient(
        app,
        client=(unique_ip, 45000),
    ) as client:
        statuses = []

        for _ in range(12):
            response = client.post(
                "/api/investigate/v2",
                json={"url": "https://example.com"},
                headers={"Origin": ALLOWED_ORIGIN},
            )
            statuses.append(response.status_code)

        assert statuses[:10] == [200] * 10, statuses
        assert statuses[10:] == [429, 429], statuses



def test_v2_does_not_create_session():
    with TestClient(app) as client:
        response = client.post(
            "/api/investigate/v2",
            json={"url": "https://example.com"},
            headers={"Origin": ALLOWED_ORIGIN},
        )

        assert response.status_code in {200, 429}

        if response.status_code == 200:
            assert "phantomlink_session" not in response.cookies


def test_v2_result_does_not_expose_session_token():
    with TestClient(app) as client:
        response = client.post(
            "/api/investigate/v2",
            json={"url": "https://example.com"},
            headers={"Origin": ALLOWED_ORIGIN},
        )

        assert response.status_code in {200, 429}

        if response.status_code == 200:
            data = response.json()

            assert "session_token" not in data
            assert "token_hash" not in data
            assert "session_id" not in data
