from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, func, or_
from sqlmodel import Session, select

from src.database.postgres.models.db_models import Market, MarketImage, PendingImage
from src.downstream.google.google_places_client import GooglePlacesClient
from src.module.market.schema.market_schema import (
    MarketCreateRequest,
    MarketListResponse,
    MarketResponse,
    MarketSearchFilters,
    MarketUpdateRequest,
)


class MarketService:
    def __init__(self, google_places_client: GooglePlacesClient):
        self.google_places_client = google_places_client

    def create_market(
        self, db: Session, user_id: UUID, request: MarketCreateRequest
    ) -> MarketResponse:
        enriched_location = self.google_places_client.validate_and_enrich_location(
            request.google_place_id, request.location_text
        )

        market_data = request.model_dump(
            exclude={"google_place_id", "location_text", "image_urls"}
        )
        market_data.update(enriched_location)
        market_data["organizer_user_id"] = user_id

        market = Market(**market_data)
        db.add(market)
        db.commit()
        db.refresh(market)

        if request.image_urls:
            for idx, image_url in enumerate(request.image_urls):
                market_image = MarketImage(
                    market_id=market.id, image_url=image_url, sort_order=idx
                )
                db.add(market_image)

                pending_images = db.exec(
                    select(PendingImage).where(PendingImage.image_url == image_url)
                ).all()
                for pending in pending_images:
                    db.delete(pending)

            db.commit()

        if request.logo_url:
            pending_logos = db.exec(
                select(PendingImage).where(PendingImage.image_url == request.logo_url)
            ).all()
            for pending in pending_logos:
                db.delete(pending)
            db.commit()

        return self._get_market_with_images(db, market.id)

    def get_market_by_id(self, db: Session, market_id: UUID) -> MarketResponse:
        market = db.get(Market, market_id)
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")

        return self._get_market_with_images(db, market_id)

    def search_markets(
        self, db: Session, filters: MarketSearchFilters
    ) -> MarketListResponse:
        query = select(Market)

        conditions = []

        if filters.city:
            conditions.append(Market.city.ilike(f"%{filters.city}%"))

        if filters.country:
            conditions.append(Market.country.ilike(f"%{filters.country}%"))

        if filters.is_published is not None:
            conditions.append(Market.is_published == filters.is_published)

        if filters.start_date_from:
            conditions.append(
                or_(
                    Market.start_date >= filters.start_date_from,
                    Market.start_date.is_(None),
                )
            )

        if filters.start_date_to:
            conditions.append(
                or_(
                    Market.start_date <= filters.start_date_to,
                    Market.start_date.is_(None),
                )
            )

        if filters.end_date_from:
            conditions.append(
                or_(
                    Market.end_date >= filters.end_date_from,
                    Market.end_date.is_(None),
                )
            )

        if filters.end_date_to:
            conditions.append(
                or_(
                    Market.end_date <= filters.end_date_to,
                    Market.end_date.is_(None),
                )
            )

        if filters.latitude and filters.longitude and filters.radius_km:
            earth_radius_km = 6371.0
            lat_rad = func.radians(filters.latitude)
            lon_rad = func.radians(filters.longitude)
            market_lat_rad = func.radians(Market.latitude)
            market_lon_rad = func.radians(Market.longitude)

            haversine = (
                func.sin((market_lat_rad - lat_rad) / 2) ** 2
                + func.cos(lat_rad)
                * func.cos(market_lat_rad)
                * func.sin((market_lon_rad - lon_rad) / 2) ** 2
            )
            distance = 2 * earth_radius_km * func.asin(func.sqrt(haversine))

            conditions.append(
                and_(
                    Market.latitude.isnot(None),
                    Market.longitude.isnot(None),
                    distance <= filters.radius_km,
                )
            )

        if conditions:
            query = query.where(and_(*conditions))

        total_query = select(func.count()).select_from(Market)
        if conditions:
            total_query = total_query.where(and_(*conditions))

        total = db.exec(total_query).one()

        query = query.order_by(Market.created_at.desc())
        query = query.offset(filters.offset).limit(filters.limit)

        markets = db.exec(query).all()

        return MarketListResponse(
            markets=[MarketResponse.model_validate(market) for market in markets],
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )

    def update_market(
        self,
        db: Session,
        market_id: UUID,
        user_id: UUID,
        request: MarketUpdateRequest,
    ) -> MarketResponse:
        market = db.get(Market, market_id)
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")

        if market.organizer_user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to update this market",
            )

        update_data = request.model_dump(exclude_unset=True)

        if "google_place_id" in update_data and update_data["google_place_id"]:
            enriched_location = self.google_places_client.validate_and_enrich_location(
                update_data["google_place_id"],
                update_data.get("location_text"),
            )
            update_data.update(enriched_location)

        image_urls = update_data.pop("image_urls", None)

        for key, value in update_data.items():
            setattr(market, key, value)

        db.add(market)
        db.commit()
        db.refresh(market)

        if image_urls is not None:
            existing_images = db.exec(
                select(MarketImage).where(MarketImage.market_id == market_id)
            ).all()
            for img in existing_images:
                db.delete(img)

            for idx, image_url in enumerate(image_urls):
                market_image = MarketImage(
                    market_id=market.id, image_url=image_url, sort_order=idx
                )
                db.add(market_image)

                pending_images = db.exec(
                    select(PendingImage).where(PendingImage.image_url == image_url)
                ).all()
                for pending in pending_images:
                    db.delete(pending)

            db.commit()

        if "logo_url" in update_data and update_data["logo_url"]:
            pending_logos = db.exec(
                select(PendingImage).where(
                    PendingImage.image_url == update_data["logo_url"]
                )
            ).all()
            for pending in pending_logos:
                db.delete(pending)
            db.commit()

        return self._get_market_with_images(db, market.id)

    def delete_market(self, db: Session, market_id: UUID, user_id: UUID) -> None:
        market = db.get(Market, market_id)
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")

        if market.organizer_user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to delete this market",
            )

        db.delete(market)
        db.commit()

    def _get_market_with_images(self, db: Session, market_id: UUID) -> MarketResponse:
        from src.module.market.schema.market_schema import MarketImageResponse

        market = db.get(Market, market_id)
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")

        images_query = (
            select(MarketImage)
            .where(MarketImage.market_id == market_id)
            .order_by(MarketImage.sort_order.asc().nulls_last())
        )
        images = db.exec(images_query).all()

        market_dict = market.model_dump()
        market_dict["images"] = [
            MarketImageResponse.model_validate(img.model_dump()) for img in images
        ]

        return MarketResponse.model_validate(market_dict)

    def get_orphaned_images(
        self, db: Session, older_than_hours: int = 24
    ) -> list[PendingImage]:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=older_than_hours)

        orphaned = db.exec(
            select(PendingImage).where(PendingImage.created_at < cutoff_time)
        ).all()

        return orphaned
