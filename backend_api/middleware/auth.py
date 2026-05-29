"""
backend_api/middleware/auth.py — AI Career Copilot
FastAPI dependency that extracts and validates a Supabase JWT.

Usage in a route:
    @router.post("/upload-resume")
    async def upload(user_id: str = Depends(require_user), ...):
        ...  # user_id is guaranteed to be a valid UUID string

For routes that optionally save to the database when authenticated:
    @router.post("/match-jd")
    async def match(user_id: str | None = Depends(optional_user), ...):
        if user_id:
            # save to db
"""

from fastapi import Depends, Header, HTTPException, status
from typing import Optional

from app.config.supabase import get_supabase_client


def _verify_token(token: str) -> str:
    """
    Validate a Supabase JWT by calling the Supabase auth API.
    Returns the user's UUID string on success, raises HTTPException on failure.
    """
    try:
        client = get_supabase_client()
        response = client.auth.get_user(token)
        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        return str(response.user.id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {exc}",
        )


async def require_user(
    authorization: str = Header(..., description="Bearer <supabase_jwt>"),
) -> str:
    """FastAPI dependency — raises 401 if no valid Bearer token is provided."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be 'Bearer <token>'",
        )
    token = authorization.removeprefix("Bearer ").strip()
    return _verify_token(token)


async def optional_user(
    authorization: Optional[str] = Header(None),
) -> Optional[str]:
    """
    FastAPI dependency — returns the user_id when a valid JWT is present,
    None when the request is unauthenticated.  Routes use this to save to the
    database when the user is logged in while still working when they are not.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ").strip()
    try:
        return _verify_token(token)
    except HTTPException:
        return None
