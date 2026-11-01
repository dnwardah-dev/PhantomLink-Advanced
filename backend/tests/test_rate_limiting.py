import pytest
from fastapi.testclient import TestClient

from main import app, limiter


@pytest.fixture
def client():
    # Use an isolated rate-limit counter for each test.
    limiter.reset()
    with TestClient(app, headers={"Origin": "http://127.0.0.1:5173"}) as test_client:
        yield test_client
    limiter.reset()


@pytest.mark.parametrize(
    "endpoint,method,limit",
    [
        ("/api/analyze", "post", 20),
        ("/api/investigate", "post", 10),
        ("/api/dns-intelligence", "post", 10),
        ("/api/history", "get", 30),
    ],
)
def test_rate_limit_returns_429(client, endpoint, method, limit):
    """
    Invalid URL payloads are intentional:
    they exercise API rate limiting without performing DNS lookups
    or saving investigation records.
    """
    responses = []

    for _ in range(limit + 1):
        if method == "post":
            response = client.post(
                endpoint,
                json={"url": "javascript:alert(1)"},
            )
        else:
            response = client.get(endpoint, params={"limit": 1})

        responses.append(response)

    expected_status = 401 if method == "get" else 422

    assert all(
        response.status_code == expected_status
        for response in responses[:limit]
    ), (
        endpoint,
        [response.status_code for response in responses],
    )

    assert responses[-1].status_code == 429, (
        endpoint,
        responses[-1].status_code,
        responses[-1].text,
    )


def test_history_limit_rejects_out_of_range_values(client):
    for limit in (0, -1, 101):
        response = client.get(
            "/api/history",
            params={"limit": limit},
        )
        assert response.status_code == 422
