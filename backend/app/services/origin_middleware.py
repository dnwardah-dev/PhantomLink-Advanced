
"""Origin protection for state-changing browser requests."""

from fastapi import Request
from starlette.responses import JSONResponse

from app.services.origin_security import is_allowed_browser_request


async def origin_protection(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")

        if not is_allowed_browser_request(origin, referer):
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Request origin is not allowed."
                },
            )

    return await call_next(request)
