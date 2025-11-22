from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, func
from sqlmodel import Session, select

from src.common.utils.s3_url import convert_s3_url_to_public_url
from src.database.postgres.models.db_models import Business, BusinessImage, PendingImage
from src.module.business.schema.business_schema import (
    BusinessCreateRequest,
    BusinessListResponse,
    BusinessResponse,
    BusinessSearchFilters,
    BusinessSearchResponse,
    BusinessUpdateRequest,
)
from src.module.review.service.review_service import ReviewService


class BusinessService:
    def __init__(self, review_service: ReviewService):
        self.review_service = review_service

    def create_business(
        self, db: Session, user_id: UUID, request: BusinessCreateRequest
    ) -> BusinessResponse:
        business_data = request.model_dump(exclude={"image_urls"})
        business_data["owner_user_id"] = user_id

        business = Business(**business_data)
        db.add(business)
        db.commit()
        db.refresh(business)

        if request.image_urls:
            for idx, image_url in enumerate(request.image_urls):
                business_image = BusinessImage(
                    business_id=business.id, image_url=image_url, sort_order=idx
                )
                db.add(business_image)

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

        return self._get_business_with_images(db, business.id)

    def get_business_by_id(self, db: Session, business_id: UUID) -> BusinessResponse:
        business = db.get(Business, business_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        return self._get_business_with_images(db, business_id)

    def search_businesses(
        self, db: Session, filters: BusinessSearchFilters
    ) -> BusinessListResponse:
        query = select(Business)

        conditions = []

        if filters.category:
            conditions.append(Business.category.ilike(f"%{filters.category}%"))

        if conditions:
            query = query.where(and_(*conditions))

        total_query = select(func.count()).select_from(Business)
        if conditions:
            total_query = total_query.where(and_(*conditions))

        total = db.exec(total_query).one()

        query = query.order_by(Business.created_at.desc())
        query = query.offset(filters.offset).limit(filters.limit)

        businesses = db.exec(query).all()

        business_ids = [business.id for business in businesses]
        review_stats = self.review_service.get_batch_review_stats(
            db, "business", business_ids
        )

        business_responses = []
        for business in businesses:
            review_count, average_rating = review_stats.get(business.id, (0, None))
            business_responses.append(
                BusinessSearchResponse(
                    id=business.id,
                    shop_name=business.shop_name,
                    category=business.category,
                    logo_url=business.logo_url,
                    review_count=review_count,
                    average_rating=average_rating,
                )
            )

        return BusinessListResponse(
            businesses=business_responses,
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )

    def update_business(
        self,
        db: Session,
        business_id: UUID,
        user_id: UUID,
        request: BusinessUpdateRequest,
    ) -> BusinessResponse:
        business = db.get(Business, business_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        if business.owner_user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to update this business",
            )

        update_data = request.model_dump(exclude_unset=True)

        image_urls = update_data.pop("image_urls", None)

        for key, value in update_data.items():
            setattr(business, key, value)

        db.add(business)
        db.commit()
        db.refresh(business)

        if image_urls is not None:
            existing_images = db.exec(
                select(BusinessImage).where(BusinessImage.business_id == business_id)
            ).all()
            for img in existing_images:
                db.delete(img)

            for idx, image_url in enumerate(image_urls):
                business_image = BusinessImage(
                    business_id=business.id, image_url=image_url, sort_order=idx
                )
                db.add(business_image)

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

        return self._get_business_with_images(db, business.id)

    def delete_business(self, db: Session, business_id: UUID, user_id: UUID) -> None:
        business = db.get(Business, business_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        if business.owner_user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to delete this business",
            )

        db.delete(business)
        db.commit()

    def get_my_businesses(
        self, db: Session, user_id: UUID, limit: int = 20, offset: int = 0
    ) -> BusinessListResponse:
        query = select(Business).where(Business.owner_user_id == user_id)

        total_query = (
            select(func.count())
            .select_from(Business)
            .where(Business.owner_user_id == user_id)
        )
        total = db.exec(total_query).one()

        query = query.order_by(Business.created_at.desc())
        query = query.offset(offset).limit(limit)

        businesses = db.exec(query).all()

        business_ids = [business.id for business in businesses]
        review_stats = self.review_service.get_batch_review_stats(
            db, "business", business_ids
        )

        business_responses = []
        for business in businesses:
            review_count, average_rating = review_stats.get(business.id, (0, None))
            logo_url = (
                convert_s3_url_to_public_url(business.logo_url)
                if business.logo_url
                else None
            )
            business_responses.append(
                BusinessSearchResponse(
                    id=business.id,
                    shop_name=business.shop_name,
                    category=business.category,
                    logo_url=logo_url,
                    review_count=review_count,
                    average_rating=average_rating,
                )
            )

        return BusinessListResponse(
            businesses=business_responses,
            total=total,
            limit=limit,
            offset=offset,
        )

    def _get_business_with_images(
        self, db: Session, business_id: UUID
    ) -> BusinessResponse:
        from src.module.business.schema.business_schema import BusinessImageResponse

        business = db.get(Business, business_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        images_query = (
            select(BusinessImage)
            .where(BusinessImage.business_id == business_id)
            .order_by(BusinessImage.sort_order.asc().nulls_last())
        )
        images = db.exec(images_query).all()

        review_count, average_rating = self.review_service._get_review_stats_internal(
            db, "business", business_id
        )

        business_dict = business.model_dump()
        if business_dict.get("logo_url"):
            business_dict["logo_url"] = convert_s3_url_to_public_url(
                business_dict["logo_url"]
            )
        business_dict["images"] = [
            BusinessImageResponse(
                id=img.id,
                business_id=img.business_id,
                image_url=convert_s3_url_to_public_url(img.image_url),
                caption=img.caption,
                sort_order=img.sort_order,
            )
            for img in images
        ]
        business_dict["review_count"] = review_count
        business_dict["average_rating"] = average_rating

        return BusinessResponse.model_validate(business_dict)
