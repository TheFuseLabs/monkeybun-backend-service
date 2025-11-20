from typing import Annotated

from fastapi import Depends

from src.downstream.supabase.dependency import get_supabase_admin_client
from src.downstream.supabase.supabase_admin_client import SupabaseAdminClient
from src.module.review.service.review_service import ReviewService


def get_review_service(
    supabase_admin_client: Annotated[
        SupabaseAdminClient, Depends(get_supabase_admin_client)
    ],
) -> ReviewService:
    return ReviewService(supabase_admin_client)


ReviewServiceDep = Annotated[ReviewService, Depends(get_review_service)]

