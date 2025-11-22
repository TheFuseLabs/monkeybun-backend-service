from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException

from src.database.dependency.db_dependency import DatabaseDep
from src.database.postgres.models.db_models import Business
from src.module.auth.dependency.auth_dependency import get_current_user
from src.module.business.service.business_service import BusinessService
from src.module.review.dependency.review_dependency import get_review_service
from src.module.review.service.review_service import ReviewService


def get_business_service(
    review_service: Annotated[ReviewService, Depends(get_review_service)],
) -> BusinessService:
    return BusinessService(review_service)


BusinessServiceDep = Annotated[BusinessService, Depends(get_business_service)]


def verify_business_ownership(
    business_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    db: DatabaseDep,
) -> Business:
    business = db.get(Business, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    if business.owner_user_id != current_user:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this business",
        )

    return business


BusinessOwnershipDep = Annotated[Business, Depends(verify_business_ownership)]
