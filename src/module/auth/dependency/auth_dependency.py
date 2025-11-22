from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.module.auth.guard.auth_guard import optional_security, security, verify_jwt


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_jwt(credentials)
    user_id_value = payload.get("sub")
    if not user_id_value:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="User ID not found in token")

    try:
        return UUID(user_id_value)
    except (ValueError, TypeError):
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Invalid user ID format in token")


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
) -> Optional[UUID]:
    if not credentials or not credentials.credentials:
        return None

    try:
        payload = verify_jwt(credentials)
        user_id_value = payload.get("sub")
        if not user_id_value:
            return None

        try:
            return UUID(user_id_value)
        except (ValueError, TypeError):
            return None
    except (HTTPException, Exception):
        return None
