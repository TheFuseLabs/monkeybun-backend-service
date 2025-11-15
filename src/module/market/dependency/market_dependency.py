from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException

from src.database.dependency.db_dependency import DatabaseDep
from src.database.postgres.models.db_models import Market
from src.downstream.google.dependency import get_google_places_client
from src.downstream.google.google_places_client import GooglePlacesClient
from src.module.auth.dependency.auth_dependency import get_current_user
from src.module.market.service.market_service import MarketService
from src.module.review.dependency.review_dependency import get_review_service
from src.module.review.service.review_service import ReviewService


def get_market_service(
    google_places_client: Annotated[
        GooglePlacesClient, Depends(get_google_places_client)
    ],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
) -> MarketService:
    return MarketService(google_places_client, review_service)


MarketServiceDep = Annotated[MarketService, Depends(get_market_service)]


def verify_market_ownership(
    market_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    db: DatabaseDep,
) -> Market:
    market = db.get(Market, market_id)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")

    if market.organizer_user_id != current_user:
        raise HTTPException(
            status_code=403, detail="You do not have permission to access this market"
        )

    return market


MarketOwnershipDep = Annotated[Market, Depends(verify_market_ownership)]
