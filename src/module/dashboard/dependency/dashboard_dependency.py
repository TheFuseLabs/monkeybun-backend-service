from typing import Annotated

from fastapi import Depends

from src.module.dashboard.service.dashboard_service import DashboardService


def get_dashboard_service() -> DashboardService:
    return DashboardService()


DashboardServiceDep = Annotated[DashboardService, Depends(get_dashboard_service)]

