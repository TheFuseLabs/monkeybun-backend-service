from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.common.logger import logger
from src.common.utils.response import Response, StandardResponse, Status
from src.database.dependency.db_dependency import DatabaseDep
from src.database.postgres.models.db_models import Business, BusinessImage
from src.module.auth.dependency.auth_dependency import get_current_user, get_optional_user
from src.module.business.dependency.business_dependency import BusinessServiceDep
from src.module.business.schema.business_schema import (
    BusinessCreateRequest,
    BusinessImageResponse,
    BusinessImageUpdateRequest,
    BusinessSearchFilters,
    BusinessUpdateRequest,
)

router = APIRouter(prefix="/business", tags=["business"])


@router.post("", status_code=Status.CREATED)
def create_business(
    request: BusinessCreateRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    business_service: BusinessServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Creating business '{request.shop_name}' by user {current_user}")
    business = business_service.create_business(db, current_user, request)
    return Response.success(
        message="Business created successfully",
        data=business.model_dump(mode="json"),
        status_code=Status.CREATED,
    )


@router.get("/my-businesses")
def get_my_businesses(
    business_service: BusinessServiceDep,
    db: DatabaseDep,
    current_user: Annotated[UUID, Depends(get_current_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> StandardResponse:
    logger.info(
        f"Retrieving businesses for user {current_user} - limit: {limit}, offset: {offset}"
    )
    result = business_service.get_my_businesses(db, current_user, limit, offset)
    return Response.success(
        message="Businesses retrieved successfully",
        data=result.model_dump(mode="json"),
    )


@router.get("/{business_id}")
def get_business(
    business_id: UUID,
    business_service: BusinessServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Retrieving business {business_id}")
    business = business_service.get_business_by_id(db, business_id)
    return Response.success(
        message="Business retrieved successfully",
        data=business.model_dump(mode="json"),
    )


@router.get("")
def search_businesses(
    business_service: BusinessServiceDep,
    db: DatabaseDep,
    current_user: Annotated[UUID | None, Depends(get_optional_user)] = None,
    category: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> StandardResponse:
    logger.info(
        f"Searching businesses - category: {category}, limit: {limit}, offset: {offset}"
    )
    filters = BusinessSearchFilters(
        category=category,
        limit=limit,
        offset=offset,
    )

    result = business_service.search_businesses(db, filters, current_user)
    return Response.success(
        message="Businesses retrieved successfully",
        data=result.model_dump(mode="json"),
    )


@router.put("/{business_id}")
def update_business(
    business_id: UUID,
    request: BusinessUpdateRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    business_service: BusinessServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Updating business {business_id} by user {current_user}")
    business = business_service.update_business(db, business_id, current_user, request)
    return Response.success(
        message="Business updated successfully",
        data=business.model_dump(mode="json"),
    )


@router.delete("/{business_id}", status_code=Status.NO_CONTENT)
def delete_business(
    business_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    business_service: BusinessServiceDep,
    db: DatabaseDep,
):
    logger.info(f"Deleting business {business_id} by user {current_user}")
    business_service.delete_business(db, business_id, current_user)
    return Response.no_content()


@router.put("/{business_id}/images/{image_id}")
def update_business_image(
    business_id: UUID,
    image_id: UUID,
    request: BusinessImageUpdateRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(
        f"Updating image {image_id} for business {business_id} by user {current_user}"
    )
    business = db.get(Business, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    if business.owner_user_id != current_user:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to update images for this business",
        )

    business_image = db.get(BusinessImage, image_id)
    if not business_image or business_image.business_id != business_id:
        raise HTTPException(status_code=404, detail="Image not found")

    if request.caption is not None:
        business_image.caption = request.caption
    if request.sort_order is not None:
        business_image.sort_order = request.sort_order

    db.add(business_image)
    db.commit()
    db.refresh(business_image)

    return Response.success(
        message="Image updated successfully",
        data=BusinessImageResponse.model_validate(
            business_image.model_dump()
        ).model_dump(mode="json"),
    )


@router.delete("/{business_id}/images/{image_id}", status_code=Status.NO_CONTENT)
def delete_business_image(
    business_id: UUID,
    image_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    db: DatabaseDep,
):
    logger.info(
        f"Deleting image {image_id} from business {business_id} by user {current_user}"
    )
    business = db.get(Business, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    if business.owner_user_id != current_user:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete images from this business",
        )

    business_image = db.get(BusinessImage, image_id)
    if not business_image or business_image.business_id != business_id:
        raise HTTPException(status_code=404, detail="Image not found")

    db.delete(business_image)
    db.commit()

    return Response.no_content()
