from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, exists, func, or_
from sqlmodel import Session, select

from src.common.utils.s3_url import convert_s3_url_to_public_url
from src.database.postgres.models.db_models import (
    Application,
    Business,
    Market,
    MarketAttendance,
    MarketFavorite,
    MarketImage,
    PendingImage,
)
from src.downstream.google.google_places_client import GooglePlacesClient
from src.module.market.schema.market_schema import (
    MarketCreateRequest,
    MarketListResponse,
    MarketResponse,
    MarketSearchFilters,
    MarketSearchResponse,
    MarketUpdateRequest,
)
from src.module.review.service.review_service import ReviewService


class MarketService:
    def __init__(
        self, google_places_client: GooglePlacesClient, review_service: ReviewService
    ):
        self.google_places_client = google_places_client
        self.review_service = review_service

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
        self, db: Session, filters: MarketSearchFilters, user_id: Optional[UUID] = None
    ) -> MarketListResponse:
        filter_conditions = []

        if filters.city:
            filter_conditions.append(Market.city.ilike(f"%{filters.city}%"))

        if filters.country:
            filter_conditions.append(Market.country.ilike(f"%{filters.country}%"))

        if filters.is_published is not None:
            filter_conditions.append(Market.is_published == filters.is_published)

        if filters.start_date_from:
            filter_conditions.append(
                or_(
                    Market.start_date >= filters.start_date_from,
                    Market.start_date.is_(None),
                )
            )

        if filters.start_date_to:
            filter_conditions.append(
                or_(
                    Market.start_date <= filters.start_date_to,
                    Market.start_date.is_(None),
                )
            )

        if filters.end_date_from:
            filter_conditions.append(
                or_(
                    Market.end_date >= filters.end_date_from,
                    Market.end_date.is_(None),
                )
            )

        if filters.end_date_to:
            filter_conditions.append(
                or_(
                    Market.end_date <= filters.end_date_to,
                    Market.end_date.is_(None),
                )
            )

        if filters.aesthetic:
            filter_conditions.append(Market.aesthetic.ilike(f"%{filters.aesthetic}%"))

        if filters.market_size:
            filter_conditions.append(Market.market_size == filters.market_size)

        if filters.is_free is not None:
            filter_conditions.append(Market.is_free == filters.is_free)

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

            filter_conditions.append(
                and_(
                    Market.latitude.isnot(None),
                    Market.longitude.isnot(None),
                    distance <= filters.radius_km,
                )
            )

        base_condition = (
            Market.organizer_user_id != user_id if user_id is not None else None
        )

        favorite_exists = None
        if user_id is not None:
            favorite_exists = exists(
                select(MarketFavorite.id).where(
                    and_(
                        MarketFavorite.market_id == Market.id,
                        MarketFavorite.user_id == user_id,
                    )
                )
            )

        query = select(Market)
        where_clause = None

        has_filters = len(filter_conditions) > 0

        if base_condition is not None and has_filters and favorite_exists is not None:
            filter_condition = (
                filter_conditions[0]
                if len(filter_conditions) == 1
                else and_(*filter_conditions)
            )
            where_clause = or_(and_(base_condition, filter_condition), favorite_exists)
        elif base_condition is not None and has_filters:
            where_clause = and_(base_condition, *filter_conditions)
        elif base_condition is not None and favorite_exists is not None:
            where_clause = or_(base_condition, favorite_exists)
        elif base_condition is not None:
            where_clause = base_condition
        elif has_filters and favorite_exists is not None:
            filter_condition = (
                filter_conditions[0]
                if len(filter_conditions) == 1
                else and_(*filter_conditions)
            )
            where_clause = or_(filter_condition, favorite_exists)
        elif has_filters:
            where_clause = (
                filter_conditions[0]
                if len(filter_conditions) == 1
                else and_(*filter_conditions)
            )
        elif favorite_exists is not None:
            where_clause = favorite_exists

        if where_clause is not None:
            query = query.where(where_clause)

        total_query = select(func.count(Market.id))
        if where_clause is not None:
            total_query = total_query.where(where_clause)

        total = db.exec(total_query).one()

        query = query.order_by(Market.created_at.desc())
        query = query.offset(filters.offset).limit(filters.limit)

        markets = db.exec(query).all()

        market_ids = [market.id for market in markets]
        review_stats = self.review_service.get_batch_review_stats(
            db, "market", market_ids
        )

        attendance_counts_query = (
            select(
                MarketAttendance.market_id,
                func.count(MarketAttendance.id).label("count"),
            )
            .where(MarketAttendance.market_id.in_(market_ids))
            .group_by(MarketAttendance.market_id)
        )
        attendance_counts_result = db.exec(attendance_counts_query).all()
        attendance_counts = {row[0]: row[1] for row in attendance_counts_result}

        favorited_market_ids = set()
        attending_market_ids = set()
        if user_id is not None and market_ids:
            favorites_query = select(MarketFavorite.market_id).where(
                and_(
                    MarketFavorite.user_id == user_id,
                    MarketFavorite.market_id.in_(market_ids),
                )
            )
            favorited_results = db.exec(favorites_query).all()
            favorited_market_ids = {
                row[0]
                if hasattr(row, "__getitem__") and not isinstance(row, UUID)
                else row
                for row in favorited_results
            }

            attendances_query = select(MarketAttendance.market_id).where(
                and_(
                    MarketAttendance.user_id == user_id,
                    MarketAttendance.market_id.in_(market_ids),
                )
            )
            attending_results = db.exec(attendances_query).all()
            attending_market_ids = {
                row[0]
                if hasattr(row, "__getitem__") and not isinstance(row, UUID)
                else row
                for row in attending_results
            }

        first_images_query = (
            select(MarketImage)
            .where(MarketImage.market_id.in_(market_ids))
            .order_by(MarketImage.sort_order.asc().nulls_last(), MarketImage.id.asc())
        )
        all_images = db.exec(first_images_query).all()

        # Group all images by market_id
        images_by_market = {}
        first_images_by_market = {}
        for image in all_images:
            if image.market_id not in images_by_market:
                images_by_market[image.market_id] = []
            images_by_market[image.market_id].append(
                convert_s3_url_to_public_url(image.image_url)
            )
            if image.market_id not in first_images_by_market:
                first_images_by_market[image.market_id] = image

        market_responses = []
        for market in markets:
            review_count, average_rating = review_stats.get(market.id, (0, None))
            attendance_count = attendance_counts.get(market.id, 0)
            logo_url = (
                convert_s3_url_to_public_url(market.logo_url)
                if market.logo_url
                else None
            )
            first_image = first_images_by_market.get(market.id)
            image_url = (
                convert_s3_url_to_public_url(first_image.image_url)
                if first_image
                else logo_url
            )

            # Get all images for this market
            market_images = images_by_market.get(market.id, [])

            is_favorited = (
                market.id in favorited_market_ids if user_id is not None else None
            )
            is_attending = (
                market.id in attending_market_ids if user_id is not None else None
            )

            market_responses.append(
                MarketSearchResponse(
                    id=market.id,
                    market_name=market.market_name,
                    location_text=market.location_text,
                    city=market.city,
                    country=market.country,
                    latitude=market.latitude,
                    longitude=market.longitude,
                    formatted_address=market.formatted_address,
                    start_date=market.start_date,
                    end_date=market.end_date,
                    logo_url=logo_url,
                    image_url=image_url,
                    review_count=review_count,
                    average_rating=average_rating,
                    aesthetic=market.aesthetic,
                    market_size=market.market_size,
                    is_free=market.is_free,
                    description=market.description,
                    cost_amount=market.cost_amount,
                    cost_currency=market.cost_currency,
                    application_deadline=market.application_deadline,
                    images=market_images if market_images else None,
                    attendance_count=attendance_count,
                    is_favorited=is_favorited,
                    is_attending=is_attending,
                )
            )

        applied_market_ids = None
        if user_id is not None:
            user_businesses = db.exec(
                select(Business).where(Business.owner_user_id == user_id)
            ).all()
            if user_businesses:
                business_ids = [business.id for business in user_businesses]
                applied_applications = db.exec(
                    select(Application.market_id)
                    .where(Application.business_id.in_(business_ids))
                    .distinct()
                ).all()
                applied_market_ids = [app[0] for app in applied_applications]

        return MarketListResponse(
            markets=market_responses,
            total=total,
            limit=filters.limit,
            offset=filters.offset,
            applied_market_ids=applied_market_ids,
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

        review_count, average_rating = self.review_service._get_review_stats_internal(
            db, "market", market_id
        )

        attendance_count_query = select(func.count(MarketAttendance.id)).where(
            MarketAttendance.market_id == market_id
        )
        attendance_count = db.exec(attendance_count_query).one() or 0

        market_dict = market.model_dump()
        if market_dict.get("logo_url"):
            market_dict["logo_url"] = convert_s3_url_to_public_url(
                market_dict["logo_url"]
            )
        market_dict["images"] = [
            MarketImageResponse(
                id=img.id,
                market_id=img.market_id,
                image_url=convert_s3_url_to_public_url(img.image_url),
                caption=img.caption,
                sort_order=img.sort_order,
            )
            for img in images
        ]
        market_dict["review_count"] = review_count
        market_dict["average_rating"] = average_rating
        market_dict["attendance_count"] = attendance_count

        return MarketResponse.model_validate(market_dict)

    def get_my_markets(
        self, db: Session, user_id: UUID, limit: int = 20, offset: int = 0
    ) -> MarketListResponse:
        query = select(Market).where(Market.organizer_user_id == user_id)

        total_query = (
            select(func.count())
            .select_from(Market)
            .where(Market.organizer_user_id == user_id)
        )
        total = db.exec(total_query).one()

        query = query.order_by(Market.created_at.desc())
        query = query.offset(offset).limit(limit)

        markets = db.exec(query).all()

        market_ids = [market.id for market in markets]
        review_stats = self.review_service.get_batch_review_stats(
            db, "market", market_ids
        )

        attendance_counts_query = (
            select(
                MarketAttendance.market_id,
                func.count(MarketAttendance.id).label("count"),
            )
            .where(MarketAttendance.market_id.in_(market_ids))
            .group_by(MarketAttendance.market_id)
        )
        attendance_counts_result = db.exec(attendance_counts_query).all()
        attendance_counts = {row[0]: row[1] for row in attendance_counts_result}

        first_images_query = (
            select(MarketImage)
            .where(MarketImage.market_id.in_(market_ids))
            .order_by(MarketImage.sort_order.asc().nulls_last(), MarketImage.id.asc())
        )
        all_images = db.exec(first_images_query).all()

        # Group all images by market_id
        images_by_market = {}
        first_images_by_market = {}
        for image in all_images:
            if image.market_id not in images_by_market:
                images_by_market[image.market_id] = []
            images_by_market[image.market_id].append(
                convert_s3_url_to_public_url(image.image_url)
            )
            if image.market_id not in first_images_by_market:
                first_images_by_market[image.market_id] = image

        market_responses = []
        for market in markets:
            review_count, average_rating = review_stats.get(market.id, (0, None))
            attendance_count = attendance_counts.get(market.id, 0)
            logo_url = (
                convert_s3_url_to_public_url(market.logo_url)
                if market.logo_url
                else None
            )
            first_image = first_images_by_market.get(market.id)
            image_url = (
                convert_s3_url_to_public_url(first_image.image_url)
                if first_image
                else logo_url
            )

            # Get all images for this market
            market_images = images_by_market.get(market.id, [])

            market_responses.append(
                MarketSearchResponse(
                    id=market.id,
                    market_name=market.market_name,
                    location_text=market.location_text,
                    city=market.city,
                    country=market.country,
                    latitude=market.latitude,
                    longitude=market.longitude,
                    formatted_address=market.formatted_address,
                    start_date=market.start_date,
                    end_date=market.end_date,
                    logo_url=logo_url,
                    image_url=image_url,
                    review_count=review_count,
                    average_rating=average_rating,
                    aesthetic=market.aesthetic,
                    market_size=market.market_size,
                    is_free=market.is_free,
                    description=market.description,
                    cost_amount=market.cost_amount,
                    cost_currency=market.cost_currency,
                    application_deadline=market.application_deadline,
                    images=market_images if market_images else None,
                    attendance_count=attendance_count,
                )
            )

        return MarketListResponse(
            markets=market_responses,
            total=total,
            limit=limit,
            offset=offset,
        )

    def get_orphaned_images(
        self, db: Session, older_than_hours: int = 24
    ) -> list[PendingImage]:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=older_than_hours)

        orphaned = db.exec(
            select(PendingImage).where(PendingImage.created_at < cutoff_time)
        ).all()

        return orphaned
