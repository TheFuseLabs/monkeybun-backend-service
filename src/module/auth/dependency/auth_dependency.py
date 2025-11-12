from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from src.module.auth.guard.auth_guard import security, verify_jwt


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
