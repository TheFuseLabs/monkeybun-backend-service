from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, func
from sqlmodel import Session, select

from src.database.postgres.models.db_models import Market, MarketFavourite
from src.module.favourite.schema.favourite_schema import (
    FavouriteCreateRequest,
    FavouriteListFilters,
    FavouriteListResponse,
    FavouriteResponse,
)


class FavouriteService:
    def create_favourite(
        self, db: Session, user_id: UUID, request: FavouriteCreateRequest
    ) -> FavouriteResponse:
        market = db.get(Market, request.market_id)
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")

        existing_favourite = db.exec(
            select(MarketFavourite).where(
                and_(
                    MarketFavourite.market_id == request.market_id,
                    MarketFavourite.user_id == user_id,
                )
            )
        ).first()

        if existing_favourite:
            raise HTTPException(
                status_code=409,
                detail="Market is already favourited by this user",
            )

        favourite = MarketFavourite(market_id=request.market_id, user_id=user_id)
        db.add(favourite)
        db.commit()
        db.refresh(favourite)

        return FavouriteResponse.model_validate(favourite.model_dump())

    def delete_favourite(self, db: Session, market_id: UUID, user_id: UUID) -> None:
        favourite = db.exec(
            select(MarketFavourite).where(
                and_(
                    MarketFavourite.market_id == market_id,
                    MarketFavourite.user_id == user_id,
                )
            )
        ).first()

        if not favourite:
            raise HTTPException(status_code=404, detail="Favourite not found")

        db.delete(favourite)
        db.commit()

    def list_favourites(
        self, db: Session, filters: FavouriteListFilters
    ) -> FavouriteListResponse:
        query = select(MarketFavourite)

        conditions = []

        if filters.market_id:
            conditions.append(MarketFavourite.market_id == filters.market_id)

        if filters.user_id:
            conditions.append(MarketFavourite.user_id == filters.user_id)

        if conditions:
            query = query.where(and_(*conditions))

        total_query = select(func.count()).select_from(MarketFavourite)
        if conditions:
            total_query = total_query.where(and_(*conditions))

        total = db.exec(total_query).one()

        query = query.order_by(MarketFavourite.created_at.desc())
        query = query.offset(filters.offset).limit(filters.limit)

        favourites = db.exec(query).all()

        favourite_responses = [
            FavouriteResponse.model_validate(favourite.model_dump())
            for favourite in favourites
        ]

        return FavouriteListResponse(
            favourites=favourite_responses,
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )

    def get_my_favourites(
        self, db: Session, user_id: UUID, limit: int = 20, offset: int = 0
    ) -> FavouriteListResponse:
        filters = FavouriteListFilters(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        return self.list_favourites(db, filters)

    def is_favourited(self, db: Session, market_id: UUID, user_id: UUID) -> bool:
        favourite = db.exec(
            select(MarketFavourite).where(
                and_(
                    MarketFavourite.market_id == market_id,
                    MarketFavourite.user_id == user_id,
                )
            )
        ).first()
        return favourite is not None
