from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.common.logger import logger
from src.common.utils.response import Response, StandardResponse
from src.database.dependency.db_dependency import DatabaseDep
from src.module.auth.dependency.auth_dependency import get_current_user
from src.module.dashboard.dependency.dashboard_dependency import DashboardServiceDep

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    dashboard_service: DashboardServiceDep,
    db: DatabaseDep,
    current_user: Annotated[UUID, Depends(get_current_user)],
) -> StandardResponse:
    logger.info(f"Retrieving dashboard stats for user {current_user}")
    stats = dashboard_service.get_dashboard_stats(db, current_user)
    return Response.success(
        message="Dashboard stats retrieved successfully",
        data=stats.model_dump(mode="json"),
    )
