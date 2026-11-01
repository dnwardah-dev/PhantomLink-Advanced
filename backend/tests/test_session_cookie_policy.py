"""Session cookie policy regression tests."""

from http.cookies import SimpleCookie

from fastapi.testclient import TestClient

from main import app


ORIGIN = "http://127.0.0.1:5173"


def test_session_cookie_security_policy():
    with TestClient(app) as client:
        response = client.post(
            "/api/session",
            headers={"Origin": ORIGIN},
        )

        assert response.status_code == 200

        cookies = SimpleCookie()
        cookies.load(response.headers["set-cookie"])

        session = cookies.get("phantomlink_session")

        assert session is not None
        assert bool(session["httponly"])
        assert session["samesite"].lower() in {"lax", "strict"}
        assert session["path"] == "/"
        assert not session["domain"]
        assert int(session["max-age"]) > 0


def test_session_token_not_returned_in_json():
    with TestClient(app) as client:
        response = client.post(
            "/api/session",
            headers={"Origin": ORIGIN},
        )

        assert response.status_code == 200

        data = response.json()

        assert "token" not in data
        assert "session_token" not in data
        assert "token_hash" not in data


def test_cookie_not_readable_by_browser_javascript():
    with TestClient(app) as client:
        response = client.post(
            "/api/session",
            headers={"Origin": ORIGIN},
        )

        assert response.status_code == 200

        cookies = SimpleCookie()
        cookies.load(response.headers["set-cookie"])

        session = cookies["phantomlink_session"]

        # HttpOnly instructs compliant browsers to hide the
        # cookie from document.cookie.
        assert bool(session["httponly"])
