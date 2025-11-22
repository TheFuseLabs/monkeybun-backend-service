from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.common.logger import logger
from src.common.utils.response import Response, StandardResponse, Status
from src.database.dependency.db_dependency import DatabaseDep
from src.module.auth.dependency.auth_dependency import get_current_user
from src.module.favorite.dependency.favorite_dependency import FavoriteServiceDep
from src.module.favorite.schema.favorite_schema import FavoriteCreateRequest

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.post("", status_code=Status.CREATED)
def create_favorite(
    request: FavoriteCreateRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    favorite_service: FavoriteServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(
        f"Creating favorite for market {request.market_id} by user {current_user}"
    )
    favorite = favorite_service.create_favorite(db, current_user, request)
    return Response.success(
        message="Favorite created successfully",
        data=favorite.model_dump(mode="json"),
        status_code=Status.CREATED,
    )


@router.delete("/{market_id}", status_code=Status.NO_CONTENT)
def delete_favorite(
    market_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    favorite_service: FavoriteServiceDep,
    db: DatabaseDep,
):
    logger.info(f"Deleting favorite for market {market_id} by user {current_user}")
    favorite_service.delete_favorite(db, market_id, current_user)
    return Response.no_content()


@router.get("")
def list_favorites(
    favorite_service: FavoriteServiceDep,
    db: DatabaseDep,
    market_id: Annotated[UUID | None, Query()] = None,
    user_id: Annotated[UUID | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> StandardResponse:
    logger.info(
        f"Listing favorites - market_id: {market_id}, user_id: {user_id}, limit: {limit}, offset: {offset}"
    )
    from src.module.favorite.schema.favorite_schema import FavoriteListFilters

    filters = FavoriteListFilters(
        market_id=market_id,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )

    result = favorite_service.list_favorites(db, filters)
    return Response.success(
        message="Favorites retrieved successfully",
        data=result.model_dump(mode="json"),
    )


@router.get("/my-favorites")
def get_my_favorites(
    favorite_service: FavoriteServiceDep,
    db: DatabaseDep,
    current_user: Annotated[UUID, Depends(get_current_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> StandardResponse:
    logger.info(
        f"Retrieving favorites for user {current_user} - limit: {limit}, offset: {offset}"
    )
    result = favorite_service.get_my_favorites(db, current_user, limit, offset)
    return Response.success(
        message="Favorites retrieved successfully",
        data=result.model_dump(mode="json"),
    )


@router.get("/check/{market_id}")
def check_favorited(
    market_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    favorite_service: FavoriteServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Checking if market {market_id} is favorited by user {current_user}")
    is_favorited = favorite_service.is_favorited(db, market_id, current_user)
    return Response.success(
        message="Favorite status retrieved successfully",
        data={"is_favorited": is_favorited},
    )
