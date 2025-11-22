from typing import Any, Dict

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from src.common.config import settings

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)
_jwks_clients: Dict[str, PyJWKClient] = {}


def _get_jwks_client(jwks_url: str) -> PyJWKClient:
    if jwks_url not in _jwks_clients:
        _jwks_clients[jwks_url] = PyJWKClient(jwks_url)
    return _jwks_clients[jwks_url]


def verify_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = credentials.credentials
    try:
        header = jwt.get_unverified_header(token)
        if header.get("alg") != "ES256":
            raise HTTPException(status_code=401, detail="Unauthorized")
        if "kid" not in header:
            raise HTTPException(status_code=401, detail="Unauthorized")

        unverified = jwt.decode(token, options={"verify_signature": False})
        issuer = unverified.get("iss")
        audience = unverified.get("aud") or settings.SUPABASE_JWT_AUDIENCE

        if not (
            issuer and issuer.startswith("https://") and issuer.endswith("/auth/v1")
        ):
            raise HTTPException(status_code=401, detail="Unauthorized")

        jwks_url = f"{issuer}/.well-known/jwks.json"
        key = _get_jwks_client(jwks_url).get_signing_key_from_jwt(token).key

        payload = jwt.decode(
            token,
            key,
            algorithms=["ES256"],
            audience=settings.SUPABASE_JWT_AUDIENCE or audience,
            issuer=issuer,
            options={"require": ["exp", "iss", "aud", "sub"]},
            leeway=5,
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Unauthorized")
    except jwt.InvalidIssuerError:
        raise HTTPException(status_code=401, detail="Unauthorized")
    except jwt.InvalidAudienceError:
        raise HTTPException(status_code=401, detail="Unauthorized")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Unauthorized")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Unauthorized")
