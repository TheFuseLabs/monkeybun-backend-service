from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException

from src.database.dependency.db_dependency import DatabaseDep
from src.database.postgres.models.db_models import Application, Business, Market
from src.downstream.resend.dependency import get_resend_email_client
from src.downstream.resend.resend_email_client import ResendEmailClient
from src.downstream.supabase.dependency import get_supabase_admin_client
from src.downstream.supabase.supabase_admin_client import SupabaseAdminClient
from src.module.auth.dependency.auth_dependency import get_current_user
from src.module.application.service.application_service import ApplicationService
from src.module.application.service.email_service import ApplicationEmailService


def get_application_service(
    email_client: Annotated[ResendEmailClient, Depends(get_resend_email_client)],
    supabase_client: Annotated[SupabaseAdminClient, Depends(get_supabase_admin_client)],
) -> ApplicationService:
    email_service = ApplicationEmailService(email_client, supabase_client)
    return ApplicationService(email_service=email_service)


ApplicationServiceDep = Annotated[ApplicationService, Depends(get_application_service)]


def verify_application_ownership(
    application_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    db: DatabaseDep,
) -> Application:
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    business = db.get(Business, application.business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    if business.owner_user_id != current_user:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this application",
        )

    return application


ApplicationOwnershipDep = Annotated[Application, Depends(verify_application_ownership)]


def verify_market_organizer(
    market_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    db: DatabaseDep,
) -> Market:
    market = db.get(Market, market_id)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")

    if market.organizer_user_id != current_user:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access applications for this market",
        )

    return market


MarketOrganizerDep = Annotated[Market, Depends(verify_market_organizer)]
