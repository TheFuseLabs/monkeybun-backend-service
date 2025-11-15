from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, func
from sqlmodel import Session, select

from src.database.postgres.models.db_models import Business, Market, Review
from src.module.review.schema.review_schema import (
    ReviewCreateRequest,
    ReviewListFilters,
    ReviewListResponse,
    ReviewResponse,
    ReviewStatsResponse,
    ReviewUpdateRequest,
)


class ReviewService:
    def create_review(
        self, db: Session, user_id: UUID, request: ReviewCreateRequest
    ) -> ReviewResponse:
        if request.target_type == "market":
            target = db.get(Market, request.target_id)
            if not target:
                raise HTTPException(status_code=404, detail="Market not found")
        elif request.target_type == "business":
            target = db.get(Business, request.target_id)
            if not target:
                raise HTTPException(status_code=404, detail="Business not found")
        else:
            raise HTTPException(
                status_code=400, detail="target_type must be 'market' or 'business'"
            )

        existing_review = db.exec(
            select(Review).where(
                and_(
                    Review.author_user_id == user_id,
                    Review.target_type == request.target_type,
                    Review.target_id == request.target_id,
                )
            )
        ).first()

        if existing_review:
            raise HTTPException(
                status_code=409,
                detail="You have already reviewed this target",
            )

        review_data = request.model_dump()
        review_data["author_user_id"] = user_id

        review = Review(**review_data)
        db.add(review)
        db.commit()
        db.refresh(review)

        return ReviewResponse.model_validate(review.model_dump())

    def get_review_by_id(self, db: Session, review_id: UUID) -> ReviewResponse:
        review = db.get(Review, review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")

        return ReviewResponse.model_validate(review.model_dump())

    def list_reviews(
        self, db: Session, filters: ReviewListFilters
    ) -> ReviewListResponse:
        query = select(Review)

        conditions = []

        if filters.target_type:
            conditions.append(Review.target_type == filters.target_type)

        if filters.target_id:
            conditions.append(Review.target_id == filters.target_id)

        if filters.author_user_id:
            conditions.append(Review.author_user_id == filters.author_user_id)

        if filters.is_published is not None:
            conditions.append(Review.is_published == filters.is_published)

        if conditions:
            query = query.where(and_(*conditions))

        total_query = select(func.count()).select_from(Review)
        if conditions:
            total_query = total_query.where(and_(*conditions))

        total = db.exec(total_query).one()

        query = query.order_by(Review.created_at.desc())
        query = query.offset(filters.offset).limit(filters.limit)

        reviews = db.exec(query).all()

        review_responses = [
            ReviewResponse.model_validate(review.model_dump()) for review in reviews
        ]

        return ReviewListResponse(
            reviews=review_responses,
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )

    def update_review(
        self,
        db: Session,
        review_id: UUID,
        user_id: UUID,
        request: ReviewUpdateRequest,
    ) -> ReviewResponse:
        review = db.get(Review, review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")

        if review.author_user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to update this review",
            )

        update_data = request.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(review, key, value)

        db.add(review)
        db.commit()
        db.refresh(review)

        return ReviewResponse.model_validate(review.model_dump())

    def delete_review(self, db: Session, review_id: UUID, user_id: UUID) -> None:
        review = db.get(Review, review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")

        if review.author_user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to delete this review",
            )

        db.delete(review)
        db.commit()

    def _get_review_stats_internal(
        self, db: Session, target_type: str, target_id: UUID
    ) -> tuple[int, float | None]:
        query = select(
            func.count(Review.id).label("total_reviews"),
            func.avg(Review.rating).label("average_rating"),
        ).where(
            and_(
                Review.target_type == target_type,
                Review.target_id == target_id,
                Review.is_published == True,
            )
        )

        result = db.exec(query).one()
        total_reviews = result[0] or 0
        average_rating = float(result[1]) if result[1] is not None else None

        return (total_reviews, average_rating)

    def get_review_stats(
        self, db: Session, target_type: str, target_id: UUID
    ) -> ReviewStatsResponse:
        if target_type == "market":
            target = db.get(Market, target_id)
            if not target:
                raise HTTPException(status_code=404, detail="Market not found")
        elif target_type == "business":
            target = db.get(Business, target_id)
            if not target:
                raise HTTPException(status_code=404, detail="Business not found")
        else:
            raise HTTPException(
                status_code=400, detail="target_type must be 'market' or 'business'"
            )

        total_reviews, average_rating = self._get_review_stats_internal(
            db, target_type, target_id
        )

        return ReviewStatsResponse(
            target_type=target_type,
            target_id=target_id,
            total_reviews=total_reviews,
            average_rating=average_rating,
        )

    def get_batch_review_stats(
        self, db: Session, target_type: str, target_ids: list[UUID]
    ) -> dict[UUID, tuple[int, float | None]]:
        if not target_ids:
            return {}

        query = (
            select(
                Review.target_id,
                func.count(Review.id).label("total_reviews"),
                func.avg(Review.rating).label("average_rating"),
            )
            .where(
                and_(
                    Review.target_type == target_type,
                    Review.target_id.in_(target_ids),
                    Review.is_published == True,
                )
            )
            .group_by(Review.target_id)
        )

        results = db.exec(query).all()
        stats_map: dict[UUID, tuple[int, float | None]] = {}

        for result in results:
            target_id = result[0]
            total_reviews = result[1] or 0
            average_rating = float(result[2]) if result[2] is not None else None
            stats_map[target_id] = (total_reviews, average_rating)

        for target_id in target_ids:
            if target_id not in stats_map:
                stats_map[target_id] = (0, None)

        return stats_map

