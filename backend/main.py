from app.services.origin_middleware import origin_protection
from app.services.security_headers import apply_security_headers
import os
from app.services.security_config import get_cookie_security_config

from app.services.session_manager import (
    create_anonymous_session,
    get_session_id,
    rotate_anonymous_session,
    get_session_remaining_seconds,
)

from app.engine.threat_explainer import explain_indicators
from fastapi import FastAPI, HTTPException, Query, Request, Response
from app.services.url_validator import validate_url, URLValidationError

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Validate deployment security settings at application startup.
SECURITY_CONFIG = get_cookie_security_config()

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="PhantomLink Advanced API",
    description="Interactive Scam Investigation Platform",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


SESSION_COOKIE_NAME = "phantomlink_session"
SESSION_MAX_AGE = 7 * 24 * 60 * 60


@app.post("/api/session")
@limiter.limit("10/minute")
def initialize_session(request: Request, response: Response):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    session_id = get_session_id(token)

    if session_id is None:
        token, session_id = create_anonymous_session()

    secure_cookie = SECURITY_CONFIG["cookie_secure"]

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=max(1, get_session_remaining_seconds(session_id)),
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        path="/",
    )

    response.headers["Cache-Control"] = "no-store"

    return {
        "status": "active",
        "session_type": "anonymous",
    }


app.middleware('http')(origin_protection)

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    return apply_security_headers(
        response,
        environment=SECURITY_CONFIG["environment"],
    )



@app.post("/api/session/rotate")
@limiter.limit("5/minute")
def rotate_session(request: Request, response: Response):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    rotated = rotate_anonymous_session(token)

    if rotated is None:
        raise HTTPException(
            status_code=401,
            detail="A valid active session is required.",
        )

    new_token, session_id = rotated

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=new_token,
        max_age=max(1, get_session_remaining_seconds(session_id)),
        httponly=True,
        secure=SECURITY_CONFIG["cookie_secure"],
        samesite="lax",
        path="/",
    )

    response.headers["Cache-Control"] = "no-store"

    return {
        "status": "rotated",
        "session_type": "anonymous",
    }


@app.get("/")
def home():
    return {
        "project": "PhantomLink Advanced",
        "message": "Backend is running successfully",
        "status": "online"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PhantomLink Backend"
    }


from pydantic import BaseModel, Field
from app.engine.scam_detector import analyze_scam_risk


class AnalyzeRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


@app.post("/api/analyze")
@limiter.limit("20/minute")
def analyze_url(request: Request, payload: AnalyzeRequest):
    try:
        validated_url = validate_url(payload.url)
    except URLValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return analyze_scam_risk(validated_url)


from app.engine.report_builder import build_investigation_report


@app.post("/api/investigate")
@limiter.limit("10/minute")
def investigate_url(request: Request, response: Response, payload: AnalyzeRequest):
    try:
        validated_url = validate_url(payload.url)
    except URLValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    analysis = analyze_scam_risk(validated_url)
    report = build_investigation_report(validated_url, analysis)

    report["threat_explanations"] = explain_indicators(
        report.get("evidence", [])
    )

    if analysis["status"] == "analyzed":
        from app.database.models import save_investigation
        token = request.cookies.get(SESSION_COOKIE_NAME)
        session_id = get_session_id(token)

        if session_id is None:
            token, session_id = create_anonymous_session()

        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=token,
                max_age=max(1, get_session_remaining_seconds(session_id)),
            httponly=True,
            secure=SECURITY_CONFIG["cookie_secure"],
            samesite="lax",
            path="/",
        )
        response.headers["Cache-Control"] = "no-store"

        investigation_id = save_investigation(
            validated_url,
            analysis,
            session_id=session_id,
        )
        report["investigation"]["id"] = investigation_id

    return report


from app.database.models import get_private_investigation_history


@app.get("/api/history")
@limiter.limit("30/minute")
def investigation_history(request: Request, limit: int = Query(default=20, ge=1, le=100)):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    session_id = get_session_id(token)

    if session_id is None:
        raise HTTPException(
            status_code=401,
            detail="A valid anonymous session is required."
        )

    history = get_private_investigation_history(
        session_id=session_id,
        limit=limit,
    )

    return {
        "status": "success",
        "history": history,
    }


from app.services.dns_intelligence import inspect_dns


@app.post("/api/dns-intelligence")
@limiter.limit("10/minute")
def dns_intelligence(request: Request, payload: AnalyzeRequest):
    try:
        validated_url = validate_url(payload.url)
        return inspect_dns(validated_url)
    except URLValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# ==========================================================
# PHANTOMLINK V2 ? EXPERIMENTAL INVESTIGATION ENDPOINT
# ==========================================================

@app.post("/api/investigate/v2")
@limiter.limit("10/minute")
def investigate_url_v2(request: Request, payload: AnalyzeRequest):
    """Offline experimental investigation without database persistence."""

    from app.engine.analysis_pipeline_v2 import analyze_url_v2

    try:
        result = analyze_url_v2(payload.url)
    except URLValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return result
