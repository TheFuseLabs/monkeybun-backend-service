from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, func
from sqlmodel import Session, select

from src.database.postgres.models.db_models import Market, MarketFavorite
from src.module.favorite.schema.favorite_schema import (
    FavoriteCreateRequest,
    FavoriteListFilters,
    FavoriteListResponse,
    FavoriteResponse,
)


class FavoriteService:
    def create_favorite(
        self, db: Session, user_id: UUID, request: FavoriteCreateRequest
    ) -> FavoriteResponse:
        market = db.get(Market, request.market_id)
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")

        existing_favorite = db.exec(
            select(MarketFavorite).where(
                and_(
                    MarketFavorite.market_id == request.market_id,
                    MarketFavorite.user_id == user_id,
                )
            )
        ).first()

        if existing_favorite:
            raise HTTPException(
                status_code=409,
                detail="Market is already favorited by this user",
            )

        favorite = MarketFavorite(market_id=request.market_id, user_id=user_id)
        db.add(favorite)
        db.commit()
        db.refresh(favorite)

        return FavoriteResponse.model_validate(favorite.model_dump())

    def delete_favorite(
        self, db: Session, market_id: UUID, user_id: UUID
    ) -> None:
        favorite = db.exec(
            select(MarketFavorite).where(
                and_(
                    MarketFavorite.market_id == market_id,
                    MarketFavorite.user_id == user_id,
                )
            )
        ).first()

        if not favorite:
            raise HTTPException(status_code=404, detail="Favorite not found")

        db.delete(favorite)
        db.commit()

    def list_favorites(
        self, db: Session, filters: FavoriteListFilters
    ) -> FavoriteListResponse:
        query = select(MarketFavorite)

        conditions = []

        if filters.market_id:
            conditions.append(MarketFavorite.market_id == filters.market_id)

        if filters.user_id:
            conditions.append(MarketFavorite.user_id == filters.user_id)

        if conditions:
            query = query.where(and_(*conditions))

        total_query = select(func.count()).select_from(MarketFavorite)
        if conditions:
            total_query = total_query.where(and_(*conditions))

        total = db.exec(total_query).one()

        query = query.order_by(MarketFavorite.created_at.desc())
        query = query.offset(filters.offset).limit(filters.limit)

        favorites = db.exec(query).all()

        favorite_responses = [
            FavoriteResponse.model_validate(favorite.model_dump())
            for favorite in favorites
        ]

        return FavoriteListResponse(
            favorites=favorite_responses,
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )

    def get_my_favorites(
        self, db: Session, user_id: UUID, limit: int = 20, offset: int = 0
    ) -> FavoriteListResponse:
        filters = FavoriteListFilters(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        return self.list_favorites(db, filters)

    def is_favorited(
        self, db: Session, market_id: UUID, user_id: UUID
    ) -> bool:
        favorite = db.exec(
            select(MarketFavorite).where(
                and_(
                    MarketFavorite.market_id == market_id,
                    MarketFavorite.user_id == user_id,
                )
            )
        ).first()
        return favorite is not None
