from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.common.logger import logger
from src.common.utils.response import Response, StandardResponse, Status
from src.database.dependency.db_dependency import DatabaseDep
from src.module.attendance.dependency.attendance_dependency import AttendanceServiceDep
from src.module.attendance.schema.attendance_schema import (
    AttendanceCreateRequest,
    AttendanceListFilters,
    AttendanceUpdateRequest,
)
from src.module.auth.dependency.auth_dependency import get_current_user

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("", status_code=Status.CREATED)
def create_attendance(
    request: AttendanceCreateRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    attendance_service: AttendanceServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(
        f"Creating attendance for market {request.market_id} by user {current_user}"
    )
    attendance = attendance_service.create_attendance(db, current_user, request)
    return Response.success(
        message="Attendance created successfully",
        data=attendance.model_dump(mode="json"),
        status_code=Status.CREATED,
    )


@router.get("/my-attendances")
def get_my_attendances(
    attendance_service: AttendanceServiceDep,
    db: DatabaseDep,
    current_user: Annotated[UUID, Depends(get_current_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> StandardResponse:
    logger.info(
        f"Retrieving attendances for user {current_user} - limit: {limit}, offset: {offset}"
    )
    result = attendance_service.get_my_attendances_with_markets(
        db, current_user, limit, offset
    )
    return Response.success(
        message="Attendances retrieved successfully",
        data=result.model_dump(mode="json"),
    )


@router.get("/{attendance_id}")
def get_attendance(
    attendance_id: UUID,
    attendance_service: AttendanceServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Retrieving attendance {attendance_id}")
    attendance = attendance_service.get_attendance_by_id(db, attendance_id)
    return Response.success(
        message="Attendance retrieved successfully",
        data=attendance.model_dump(mode="json"),
    )


@router.get("")
def list_attendances(
    attendance_service: AttendanceServiceDep,
    db: DatabaseDep,
    market_id: Annotated[UUID | None, Query()] = None,
    user_id: Annotated[UUID | None, Query()] = None,
    status: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> StandardResponse:
    logger.info(
        f"Listing attendances - market_id: {market_id}, user_id: {user_id}, status: {status}, limit: {limit}, offset: {offset}"
    )
    filters = AttendanceListFilters(
        market_id=market_id,
        user_id=user_id,
        status=status,
        limit=limit,
        offset=offset,
    )

    result = attendance_service.list_attendances(db, filters)
    return Response.success(
        message="Attendances retrieved successfully",
        data=result.model_dump(mode="json"),
    )


@router.put("/{attendance_id}")
def update_attendance(
    attendance_id: UUID,
    request: AttendanceUpdateRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    attendance_service: AttendanceServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Updating attendance {attendance_id} by user {current_user}")
    attendance = attendance_service.update_attendance(
        db, attendance_id, current_user, request
    )
    return Response.success(
        message="Attendance updated successfully",
        data=attendance.model_dump(mode="json"),
    )


@router.delete("/{attendance_id}", status_code=Status.NO_CONTENT)
def delete_attendance(
    attendance_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    attendance_service: AttendanceServiceDep,
    db: DatabaseDep,
):
    logger.info(f"Deleting attendance {attendance_id} by user {current_user}")
    attendance_service.delete_attendance(db, attendance_id, current_user)
    return Response.no_content()
