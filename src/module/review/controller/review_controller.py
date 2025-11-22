from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.common.logger import logger
from src.common.utils.response import Response, StandardResponse, Status
from src.database.dependency.db_dependency import DatabaseDep
from src.module.auth.dependency.auth_dependency import get_current_user
from src.module.review.dependency.review_dependency import ReviewServiceDep
from src.module.review.schema.review_schema import (
    ReviewCreateRequest,
    ReviewListFilters,
    ReviewUpdateRequest,
)

router = APIRouter(prefix="/review", tags=["review"])


@router.post("", status_code=Status.CREATED)
def create_review(
    request: ReviewCreateRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    review_service: ReviewServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(
        f"Creating review for {request.target_type} {request.target_id} by user {current_user}"
    )
    review = review_service.create_review(db, current_user, request)
    return Response.success(
        message="Review created successfully",
        data=review.model_dump(mode="json"),
        status_code=Status.CREATED,
    )


@router.get("/{review_id}")
def get_review(
    review_id: UUID,
    review_service: ReviewServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Retrieving review {review_id}")
    review = review_service.get_review_by_id(db, review_id)
    return Response.success(
        message="Review retrieved successfully",
        data=review.model_dump(mode="json"),
    )


@router.get("")
def list_reviews(
    review_service: ReviewServiceDep,
    db: DatabaseDep,
    target_type: Annotated[str | None, Query()] = None,
    target_id: Annotated[UUID | None, Query()] = None,
    author_user_id: Annotated[UUID | None, Query()] = None,
    is_published: Annotated[bool | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> StandardResponse:
    logger.info(
        f"Listing reviews - target_type: {target_type}, target_id: {target_id}, limit: {limit}, offset: {offset}"
    )
    filters = ReviewListFilters(
        target_type=target_type,
        target_id=target_id,
        author_user_id=author_user_id,
        is_published=is_published,
        limit=limit,
        offset=offset,
    )

    result = review_service.list_reviews(db, filters)
    return Response.success(
        message="Reviews retrieved successfully",
        data=result.model_dump(mode="json"),
    )


@router.put("/{review_id}")
def update_review(
    review_id: UUID,
    request: ReviewUpdateRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    review_service: ReviewServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Updating review {review_id} by user {current_user}")
    review = review_service.update_review(db, review_id, current_user, request)
    return Response.success(
        message="Review updated successfully",
        data=review.model_dump(mode="json"),
    )


@router.delete("/{review_id}", status_code=Status.NO_CONTENT)
def delete_review(
    review_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    review_service: ReviewServiceDep,
    db: DatabaseDep,
):
    logger.info(f"Deleting review {review_id} by user {current_user}")
    review_service.delete_review(db, review_id, current_user)
    return Response.no_content()


@router.get("/stats/{target_type}/{target_id}")
def get_review_stats(
    target_type: str,
    target_id: UUID,
    review_service: ReviewServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Getting review stats for {target_type} {target_id}")
    stats = review_service.get_review_stats(db, target_type, target_id)
    return Response.success(
        message="Review stats retrieved successfully",
        data=stats.model_dump(mode="json"),
    )
