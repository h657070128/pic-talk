from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_service import AuthService

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Decode JWT and return user info. Raises 401 if invalid."""
    token = credentials.credentials
    payload = AuthService.verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> dict | None:
    """Same as above but returns None for unauthenticated requests (public endpoints)."""
    if not credentials:
        return None
    token = credentials.credentials
    payload = AuthService.verify_access_token(token)
    return payload
