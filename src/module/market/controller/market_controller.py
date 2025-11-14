from datetime import date as date_type
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.common.logger import logger
from src.common.utils.response import Response, StandardResponse, Status
from src.database.dependency.db_dependency import DatabaseDep
from src.database.postgres.models.db_models import Market, MarketImage
from src.module.auth.dependency.auth_dependency import get_current_user
from src.module.market.dependency.market_dependency import MarketServiceDep
from src.module.market.schema.market_schema import (
    MarketCreateRequest,
    MarketImageCreateRequest,
    MarketImageResponse,
    MarketImageUpdateRequest,
    MarketSearchFilters,
    MarketUpdateRequest,
)

router = APIRouter(prefix="/market", tags=["market"])


@router.post("", status_code=Status.CREATED)
def create_market(
    request: MarketCreateRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    market_service: MarketServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Creating market '{request.market_name}' by user {current_user}")
    market = market_service.create_market(db, current_user, request)
    return Response.success(
        message="Market created successfully",
        data=market.model_dump(mode="json"),
        status_code=Status.CREATED,
    )


@router.get("/{market_id}")
def get_market(
    market_id: UUID,
    market_service: MarketServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Retrieving market {market_id}")
    market = market_service.get_market_by_id(db, market_id)
    return Response.success(
        message="Market retrieved successfully",
        data=market.model_dump(mode="json"),
    )


@router.get("")
def search_markets(
    market_service: MarketServiceDep,
    db: DatabaseDep,
    city: Annotated[str | None, Query()] = None,
    country: Annotated[str | None, Query()] = None,
    is_published: Annotated[bool | None, Query()] = None,
    start_date_from: Annotated[str | None, Query()] = None,
    start_date_to: Annotated[str | None, Query()] = None,
    end_date_from: Annotated[str | None, Query()] = None,
    end_date_to: Annotated[str | None, Query()] = None,
    latitude: Annotated[float | None, Query()] = None,
    longitude: Annotated[float | None, Query()] = None,
    radius_km: Annotated[float | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> StandardResponse:
    logger.info(
        f"Searching markets - city: {city}, country: {country}, published: {is_published}, limit: {limit}, offset: {offset}"
    )
    filters = MarketSearchFilters(
        city=city,
        country=country,
        is_published=is_published,
        start_date_from=date_type.fromisoformat(start_date_from)
        if start_date_from
        else None,
        start_date_to=date_type.fromisoformat(start_date_to) if start_date_to else None,
        end_date_from=date_type.fromisoformat(end_date_from) if end_date_from else None,
        end_date_to=date_type.fromisoformat(end_date_to) if end_date_to else None,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit,
        offset=offset,
    )

    result = market_service.search_markets(db, filters)
    return Response.success(
        message="Markets retrieved successfully",
        data=result.model_dump(mode="json"),
    )


@router.put("/{market_id}")
def update_market(
    market_id: UUID,
    request: MarketUpdateRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    market_service: MarketServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Updating market {market_id} by user {current_user}")
    market = market_service.update_market(db, market_id, current_user, request)
    return Response.success(
        message="Market updated successfully",
        data=market.model_dump(mode="json"),
    )


@router.delete("/{market_id}", status_code=Status.NO_CONTENT)
def delete_market(
    market_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    market_service: MarketServiceDep,
    db: DatabaseDep,
):
    logger.info(f"Deleting market {market_id} by user {current_user}")
    market_service.delete_market(db, market_id, current_user)
    return Response.no_content()


@router.post("/{market_id}/images", status_code=Status.CREATED)
def add_market_image(
    market_id: UUID,
    request: MarketImageCreateRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Adding image to market {market_id} by user {current_user}")
    market = db.get(Market, market_id)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")

    if market.organizer_user_id != current_user:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to add images to this market",
        )

    from sqlmodel import func, select

    max_sort_order = (
        db.exec(
            select(func.max(MarketImage.sort_order)).where(
                MarketImage.market_id == market_id
            )
        ).scalar()
        or -1
    )

    market_image = MarketImage(
        market_id=market_id,
        image_url=request.image_url,
        caption=request.caption,
        sort_order=request.sort_order
        if request.sort_order is not None
        else max_sort_order + 1,
    )
    db.add(market_image)
    db.commit()
    db.refresh(market_image)

    return Response.success(
        message="Image added successfully",
        data=MarketImageResponse.model_validate(market_image.model_dump()).model_dump(
            mode="json"
        ),
        status_code=Status.CREATED,
    )


@router.get("/{market_id}/images")
def get_market_images(
    market_id: UUID,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Retrieving images for market {market_id}")
    market = db.get(Market, market_id)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")

    from sqlmodel import select

    images = db.exec(
        select(MarketImage)
        .where(MarketImage.market_id == market_id)
        .order_by(MarketImage.sort_order.asc().nulls_last())
    ).all()

    return Response.success(
        message="Images retrieved successfully",
        data=[
            MarketImageResponse.model_validate(img.model_dump()).model_dump(mode="json")
            for img in images
        ],
    )


@router.put("/{market_id}/images/{image_id}")
def update_market_image(
    market_id: UUID,
    image_id: UUID,
    request: MarketImageUpdateRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(
        f"Updating image {image_id} for market {market_id} by user {current_user}"
    )
    market = db.get(Market, market_id)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")

    if market.organizer_user_id != current_user:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to update images for this market",
        )

    market_image = db.get(MarketImage, image_id)
    if not market_image or market_image.market_id != market_id:
        raise HTTPException(status_code=404, detail="Image not found")

    if request.caption is not None:
        market_image.caption = request.caption
    if request.sort_order is not None:
        market_image.sort_order = request.sort_order

    db.add(market_image)
    db.commit()
    db.refresh(market_image)

    return Response.success(
        message="Image updated successfully",
        data=MarketImageResponse.model_validate(market_image.model_dump()).model_dump(
            mode="json"
        ),
    )


@router.delete("/{market_id}/images/{image_id}", status_code=Status.NO_CONTENT)
def delete_market_image(
    market_id: UUID,
    image_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    db: DatabaseDep,
):
    logger.info(
        f"Deleting image {image_id} from market {market_id} by user {current_user}"
    )
    market = db.get(Market, market_id)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")

    if market.organizer_user_id != current_user:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete images from this market",
        )

    market_image = db.get(MarketImage, image_id)
    if not market_image or market_image.market_id != market_id:
        raise HTTPException(status_code=404, detail="Image not found")

    db.delete(market_image)
    db.commit()

    return Response.no_content()
