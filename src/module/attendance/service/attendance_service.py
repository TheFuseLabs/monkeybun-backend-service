from datetime import date
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, func
from sqlmodel import Session, select

from src.database.postgres.models.db_models import Market, MarketAttendance
from src.common.utils.s3_url import convert_s3_url_to_public_url
from src.database.postgres.models.db_models import MarketImage
from src.module.attendance.schema.attendance_schema import (
    AttendanceCreateRequest,
    AttendanceListFilters,
    AttendanceListResponse,
    AttendanceListWithMarketsResponse,
    AttendanceResponse,
    AttendanceUpdateRequest,
    AttendanceWithMarketResponse,
)
from src.module.review.service.review_service import ReviewService


class AttendanceService:
    def __init__(self, review_service: ReviewService):
        self.review_service = review_service
    def create_attendance(
        self, db: Session, user_id: UUID, request: AttendanceCreateRequest
    ) -> AttendanceResponse:
        market = db.get(Market, request.market_id)
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")

        if market.end_date and market.end_date < date.today():
            raise HTTPException(
                status_code=400,
                detail="Cannot attend a market that has already finished",
            )

        existing_attendance = db.exec(
            select(MarketAttendance).where(
                and_(
                    MarketAttendance.market_id == request.market_id,
                    MarketAttendance.user_id == user_id,
                )
            )
        ).first()

        if existing_attendance:
            raise HTTPException(
                status_code=409,
                detail="Attendance record already exists for this market and user",
            )

        attendance_data = request.model_dump()
        attendance_data["user_id"] = user_id

        attendance = MarketAttendance(**attendance_data)
        db.add(attendance)
        db.commit()
        db.refresh(attendance)

        return AttendanceResponse.model_validate(attendance.model_dump())

    def get_attendance_by_id(
        self, db: Session, attendance_id: UUID
    ) -> AttendanceResponse:
        attendance = db.get(MarketAttendance, attendance_id)
        if not attendance:
            raise HTTPException(status_code=404, detail="Attendance not found")

        return AttendanceResponse.model_validate(attendance.model_dump())

    def list_attendances(
        self, db: Session, filters: AttendanceListFilters
    ) -> AttendanceListResponse:
        query = select(MarketAttendance)

        conditions = []

        if filters.market_id:
            conditions.append(MarketAttendance.market_id == filters.market_id)

        if filters.user_id:
            conditions.append(MarketAttendance.user_id == filters.user_id)

        if filters.status:
            conditions.append(MarketAttendance.status == filters.status)

        if conditions:
            query = query.where(and_(*conditions))

        total_query = select(func.count()).select_from(MarketAttendance)
        if conditions:
            total_query = total_query.where(and_(*conditions))

        total = db.exec(total_query).one()

        query = query.order_by(MarketAttendance.created_at.desc())
        query = query.offset(filters.offset).limit(filters.limit)

        attendances = db.exec(query).all()

        attendance_responses = [
            AttendanceResponse.model_validate(attendance.model_dump())
            for attendance in attendances
        ]

        return AttendanceListResponse(
            attendances=attendance_responses,
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )

    def update_attendance(
        self,
        db: Session,
        attendance_id: UUID,
        user_id: UUID,
        request: AttendanceUpdateRequest,
    ) -> AttendanceResponse:
        attendance = db.get(MarketAttendance, attendance_id)
        if not attendance:
            raise HTTPException(status_code=404, detail="Attendance not found")

        if attendance.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to update this attendance record",
            )

        update_data = request.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(attendance, key, value)

        db.add(attendance)
        db.commit()
        db.refresh(attendance)

        return AttendanceResponse.model_validate(attendance.model_dump())

    def delete_attendance(
        self, db: Session, attendance_id: UUID, user_id: UUID
    ) -> None:
        attendance = db.get(MarketAttendance, attendance_id)
        if not attendance:
            raise HTTPException(status_code=404, detail="Attendance not found")

        if attendance.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to delete this attendance record",
            )

        db.delete(attendance)
        db.commit()

    def get_my_attendances(
        self, db: Session, user_id: UUID, limit: int = 20, offset: int = 0
    ) -> AttendanceListResponse:
        filters = AttendanceListFilters(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        return self.list_attendances(db, filters)

    def get_my_attendances_with_markets(
        self, db: Session, user_id: UUID, limit: int = 20, offset: int = 0
    ) -> AttendanceListWithMarketsResponse:
        filters = AttendanceListFilters(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )

        query = select(MarketAttendance)
        conditions = [MarketAttendance.user_id == user_id]
        query = query.where(and_(*conditions))

        total_query = select(func.count()).select_from(MarketAttendance)
        total_query = total_query.where(and_(*conditions))
        total = db.exec(total_query).one()

        query = query.order_by(MarketAttendance.created_at.desc())
        query = query.offset(filters.offset).limit(filters.limit)
        attendances = db.exec(query).all()

        market_ids = [attendance.market_id for attendance in attendances]
        markets = {}
        if market_ids:
            review_stats = self.review_service.get_batch_review_stats(
                db, "market", market_ids
            )
            markets_query = select(Market).where(Market.id.in_(market_ids))
            markets_list = db.exec(markets_query).all()
            images_query = (
                select(MarketImage)
                .where(MarketImage.market_id.in_(market_ids))
                .order_by(MarketImage.sort_order.asc().nulls_last(), MarketImage.id.asc())
            )
            all_images = db.exec(images_query).all()
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

            for market in markets_list:
                review_count, average_rating = review_stats.get(market.id, (0, None))
                market_dict = market.model_dump()
                if market_dict.get("logo_url"):
                    market_dict["logo_url"] = convert_s3_url_to_public_url(
                        market_dict["logo_url"]
                    )
                first_image = first_images_by_market.get(market.id)
                market_dict["image_url"] = (
                    convert_s3_url_to_public_url(first_image.image_url)
                    if first_image
                    else market_dict.get("logo_url")
                )
                market_dict["images"] = images_by_market.get(market.id, [])
                market_dict["review_count"] = review_count
                market_dict["average_rating"] = average_rating
                markets[market.id] = market_dict

        attendance_responses = []
        for attendance in attendances:
            market_data = markets.get(attendance.market_id)
            attendance_responses.append(
                AttendanceWithMarketResponse(
                    id=attendance.id,
                    market_id=attendance.market_id,
                    user_id=attendance.user_id,
                    status=attendance.status,
                    calendar_event_id=attendance.calendar_event_id,
                    created_at=attendance.created_at,
                    market=market_data,
                )
            )

        return AttendanceListWithMarketsResponse(
            attendances=attendance_responses,
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )
