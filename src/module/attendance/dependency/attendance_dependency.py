from typing import Annotated

from fastapi import Depends

from src.module.attendance.service.attendance_service import AttendanceService
from src.module.review.dependency.review_dependency import ReviewServiceDep


def get_attendance_service(
    review_service: ReviewServiceDep,
) -> AttendanceService:
    return AttendanceService(review_service)


AttendanceServiceDep = Annotated[AttendanceService, Depends(get_attendance_service)]
