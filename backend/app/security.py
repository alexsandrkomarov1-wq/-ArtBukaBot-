import secrets

from fastapi import Header, HTTPException, Request, status


def require_api_token(
    request: Request,
    x_core_token: str | None = Header(default=None, alias="X-Core-Token"),
    x_actor_id: str | None = Header(default=None, alias="X-Actor-ID"),
) -> str | None:
    expected = request.app.state.api_token
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API is locked: CORE_API_TOKEN is not configured",
        )
    if not x_core_token or not secrets.compare_digest(x_core_token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid X-Core-Token header required",
        )
    return x_actor_id
