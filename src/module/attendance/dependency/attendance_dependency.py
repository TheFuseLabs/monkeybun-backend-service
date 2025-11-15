from typing import Annotated

from fastapi import Depends

from src.module.attendance.service.attendance_service import AttendanceService


def get_attendance_service() -> AttendanceService:
    return AttendanceService()


AttendanceServiceDep = Annotated[AttendanceService, Depends(get_attendance_service)]

