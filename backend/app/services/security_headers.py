"""HTTP security headers for PhantomLink API."""


def apply_security_headers(response, environment="development"):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"

    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )

    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; "
        "base-uri 'none'; "
        "frame-ancestors 'none'; "
        "form-action 'none'"
    )

    if environment == "production":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000"
        )

    return response
