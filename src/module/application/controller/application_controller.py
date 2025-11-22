from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.common.logger import logger
from src.common.utils.response import Response, StandardResponse, Status
from src.database.dependency.db_dependency import DatabaseDep
from src.database.postgres.models.db_models import ApplicationStatus, Business, Market
from src.module.application.dependency.application_dependency import (
    ApplicationServiceDep,
    MarketOrganizerDep,
)
from src.module.application.schema.application_schema import (
    ApplicationAcceptRequest,
    ApplicationConfirmRequest,
    ApplicationCreateRequest,
    ApplicationPaymentUpdateRequest,
    ApplicationRejectRequest,
    ApplicationSearchFilters,
    ApplicationUpdateRequest,
)
from src.module.auth.dependency.auth_dependency import get_current_user

router = APIRouter(prefix="/application", tags=["application"])


@router.post("", status_code=Status.CREATED)
def create_application(
    request: ApplicationCreateRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    application_service: ApplicationServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(
        f"Creating application for market {request.market_id} and business {request.business_id} by user {current_user}"
    )
    application = application_service.create_application(db, current_user, request)
    return Response.success(
        message="Application created successfully",
        data=application.model_dump(mode="json"),
        status_code=Status.CREATED,
    )


@router.get("/my-applications")
def get_my_applications(
    application_service: ApplicationServiceDep,
    db: DatabaseDep,
    current_user: Annotated[UUID, Depends(get_current_user)],
    status: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> StandardResponse:
    logger.info(
        f"Retrieving applications for user {current_user} - status: {status}, limit: {limit}, offset: {offset}"
    )

    status_enum = None
    if status:
        try:
            status_enum = ApplicationStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid status value: {status}"
            )

    result = application_service.get_my_applications(
        db, current_user, status_enum, limit, offset
    )
    return Response.success(
        message="Applications retrieved successfully",
        data=result.model_dump(mode="json"),
    )


@router.get("/{application_id}")
def get_application(
    application_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    application_service: ApplicationServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Retrieving application {application_id} by user {current_user}")
    application = application_service.get_application_by_id(db, application_id)

    business = db.get(Business, application.business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    if business.owner_user_id != current_user:
        market = db.get(Market, application.market_id)
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")

        if market.organizer_user_id != current_user:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to view this application",
            )

    return Response.success(
        message="Application retrieved successfully",
        data=application.model_dump(mode="json"),
    )


@router.get("")
def search_applications(
    application_service: ApplicationServiceDep,
    db: DatabaseDep,
    current_user: Annotated[UUID, Depends(get_current_user)],
    market_id: Annotated[UUID | None, Query()] = None,
    business_id: Annotated[UUID | None, Query()] = None,
    status: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> StandardResponse:
    logger.info(
        f"Searching applications - market_id: {market_id}, business_id: {business_id}, status: {status}, limit: {limit}, offset: {offset} by user {current_user}"
    )

    if business_id:
        business = db.get(Business, business_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        if business.owner_user_id != current_user:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to view applications for this business",
            )

    if market_id:
        market = db.get(Market, market_id)
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")
        if market.organizer_user_id != current_user:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to view applications for this market",
            )

    if not market_id and not business_id:
        raise HTTPException(
            status_code=400,
            detail="Either market_id or business_id must be provided",
        )

    status_enum = None
    if status:
        try:
            status_enum = ApplicationStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid status value: {status}"
            )

    filters = ApplicationSearchFilters(
        market_id=market_id,
        business_id=business_id,
        status=status_enum,
        limit=limit,
        offset=offset,
    )

    result = application_service.search_applications(db, filters)
    return Response.success(
        message="Applications retrieved successfully",
        data=result.model_dump(mode="json"),
    )


@router.get("/market/{market_id}")
def get_market_applications(
    market: MarketOrganizerDep,
    application_service: ApplicationServiceDep,
    db: DatabaseDep,
    status: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> StandardResponse:
    logger.info(
        f"Retrieving applications for market {market.id} - status: {status}, limit: {limit}, offset: {offset}"
    )

    status_enum = None
    if status:
        try:
            status_enum = ApplicationStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid status value: {status}"
            )

    filters = ApplicationSearchFilters(
        market_id=market.id,
        status=status_enum,
        limit=limit,
        offset=offset,
    )

    result = application_service.search_applications(db, filters)
    return Response.success(
        message="Applications retrieved successfully",
        data=result.model_dump(mode="json"),
    )


@router.put("/{application_id}")
def update_application(
    application_id: UUID,
    request: ApplicationUpdateRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    application_service: ApplicationServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Updating application {application_id} by user {current_user}")
    application = application_service.update_application(
        db, application_id, current_user, request
    )
    return Response.success(
        message="Application updated successfully",
        data=application.model_dump(mode="json"),
    )


@router.delete("/{application_id}", status_code=Status.NO_CONTENT)
def delete_application(
    application_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    application_service: ApplicationServiceDep,
    db: DatabaseDep,
):
    logger.info(f"Deleting application {application_id} by user {current_user}")
    application_service.delete_application(db, application_id, current_user)
    return Response.no_content()


@router.post("/{application_id}/accept")
def accept_application(
    application_id: UUID,
    request: ApplicationAcceptRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    application_service: ApplicationServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Accepting application {application_id} by user {current_user}")
    application = application_service.accept_application(
        db, application_id, current_user, request
    )
    return Response.success(
        message="Application accepted successfully",
        data=application.model_dump(mode="json"),
    )


@router.post("/{application_id}/reject")
def reject_application(
    application_id: UUID,
    request: ApplicationRejectRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    application_service: ApplicationServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Rejecting application {application_id} by user {current_user}")
    application = application_service.reject_application(
        db, application_id, current_user, request
    )
    return Response.success(
        message="Application rejected successfully",
        data=application.model_dump(mode="json"),
    )


@router.put("/{application_id}/payment")
def update_payment(
    application_id: UUID,
    request: ApplicationPaymentUpdateRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    application_service: ApplicationServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(
        f"Updating payment for application {application_id} by user {current_user}"
    )
    application = application_service.update_payment(
        db, application_id, current_user, request
    )
    return Response.success(
        message="Payment updated successfully",
        data=application.model_dump(mode="json"),
    )


@router.post("/{application_id}/confirm")
def confirm_application(
    application_id: UUID,
    request: ApplicationConfirmRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    application_service: ApplicationServiceDep,
    db: DatabaseDep,
) -> StandardResponse:
    logger.info(f"Confirming application {application_id} by user {current_user}")
    application = application_service.confirm_application(
        db, application_id, current_user, request
    )
    return Response.success(
        message="Application confirmed successfully",
        data=application.model_dump(mode="json"),
    )
