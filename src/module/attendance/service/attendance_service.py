from datetime import date
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, func
from sqlmodel import Session, select

from src.database.postgres.models.db_models import Market, MarketAttendance
from src.module.attendance.schema.attendance_schema import (
    AttendanceCreateRequest,
    AttendanceListFilters,
    AttendanceListResponse,
    AttendanceResponse,
    AttendanceUpdateRequest,
)


class AttendanceService:
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

