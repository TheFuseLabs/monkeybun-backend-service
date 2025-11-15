from typing import Annotated
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException

from src.common.config import settings
from src.common.utils.response import Response
from src.downstream.supabase.dependency import get_supabase_admin_client
from src.downstream.supabase.supabase_admin_client import SupabaseAdminClient
from src.module.auth.dependency.auth_dependency import get_current_user
from src.module.auth.schema.auth_schema import UserResponse, UserUpdateRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
def get_profile(
    current_user: Annotated[UUID, Depends(get_current_user)],
    supabase_admin_client: Annotated[
        SupabaseAdminClient, Depends(get_supabase_admin_client)
    ],
):
    if settings.PYTHON_ENV != "DEV":
        raise HTTPException(status_code=404, detail="Not Found")

    user = supabase_admin_client.get_user(current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    metadata = user.user_metadata or {}
    full_name = metadata.get("full_name") or metadata.get("display_name")
    avatar_url = metadata.get("avatar_url") or metadata.get("picture")

    user_response = UserResponse(
        id=UUID(user.id),
        email=user.email or "",
        full_name=full_name,
        avatar_url=avatar_url,
    )

    return Response.success(
        message="Profile retrieved",
        data=user_response.model_dump(mode="json"),
    )


@router.put("/me")
def update_profile(
    request: UserUpdateRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    supabase_admin_client: Annotated[
        SupabaseAdminClient, Depends(get_supabase_admin_client)
    ],
):
    if settings.PYTHON_ENV != "DEV":
        raise HTTPException(status_code=404, detail="Not Found")

    user = supabase_admin_client.get_user(current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_metadata = user.user_metadata or {}
    update_metadata = current_metadata.copy()

    if request.full_name is not None:
        update_metadata["full_name"] = request.full_name
    if request.avatar_url is not None:
        update_metadata["avatar_url"] = request.avatar_url

    updated_user = supabase_admin_client.update_user(current_user, update_metadata)
    if not updated_user:
        raise HTTPException(status_code=500, detail="Failed to update profile")

    metadata = updated_user.user_metadata or {}
    full_name = metadata.get("full_name") or metadata.get("display_name")
    avatar_url = metadata.get("avatar_url") or metadata.get("picture")

    user_response = UserResponse(
        id=UUID(updated_user.id),
        email=updated_user.email or "",
        full_name=full_name,
        avatar_url=avatar_url,
    )

    return Response.success(
        message="Profile updated successfully",
        data=user_response.model_dump(mode="json"),
    )


@router.post("/token")
def create_token():
    if settings.PYTHON_ENV != "DEV":
        raise HTTPException(status_code=404, detail="Not Found")

    if not settings.SUPABASE_DEV_USERNAME or not settings.SUPABASE_DEV_PASSWORD:
        raise HTTPException(status_code=500, detail="Dev credentials not configured")

    try:
        response = httpx.post(
            f"https://{settings.SUPABASE_PROJECT_REF}.supabase.co/auth/v1/token?grant_type=password",
            json={
                "email": settings.SUPABASE_DEV_USERNAME,
                "password": settings.SUPABASE_DEV_PASSWORD,
            },
            headers={
                "apikey": settings.SUPABASE_PUBLISHABLE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_PUBLISHABLE_KEY}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Authentication failed")

        token_data = response.json()
        return Response.success(
            message="Token created",
            data={"access_token": token_data.get("access_token")},
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=500, detail="Authentication service unavailable"
        )


