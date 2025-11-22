from uuid import UUID

from sqlalchemy import func
from sqlmodel import Session, select

from src.database.postgres.models.db_models import (
    Application,
    ApplicationStatus,
    Business,
    Market,
    MarketAttendance,
    Review,
)
from src.module.dashboard.schema.dashboard_schema import (
    ApplicationStats,
    DashboardStatsResponse,
)


class DashboardService:
    def get_dashboard_stats(self, db: Session, user_id: UUID) -> DashboardStatsResponse:
        businesses_count = db.exec(
            select(func.count())
            .select_from(Business)
            .where(Business.owner_user_id == user_id)
        ).one()

        markets_count = db.exec(
            select(func.count())
            .select_from(Market)
            .where(Market.organizer_user_id == user_id)
        ).one()

        user_businesses = db.exec(
            select(Business).where(Business.owner_user_id == user_id)
        ).all()
        business_ids = [business.id for business in user_businesses]

        applications_total = 0
        applications_applied = 0
        applications_accepted = 0
        applications_declined = 0
        applications_confirmed = 0

        if business_ids:
            applications_query = select(Application).where(
                Application.business_id.in_(business_ids)
            )
            applications = db.exec(applications_query).all()

            applications_total = len(applications)
            for app in applications:
                if app.status == ApplicationStatus.applied:
                    applications_applied += 1
                elif app.status == ApplicationStatus.accepted:
                    applications_accepted += 1
                elif app.status == ApplicationStatus.declined:
                    applications_declined += 1
                elif app.status == ApplicationStatus.confirmed:
                    applications_confirmed += 1

        attendances_count = db.exec(
            select(func.count())
            .select_from(MarketAttendance)
            .where(MarketAttendance.user_id == user_id)
        ).one()

        reviews_written_count = db.exec(
            select(func.count())
            .select_from(Review)
            .where(Review.author_user_id == user_id)
        ).one()

        return DashboardStatsResponse(
            businesses_count=businesses_count,
            markets_count=markets_count,
            applications=ApplicationStats(
                total=applications_total,
                applied=applications_applied,
                accepted=applications_accepted,
                declined=applications_declined,
                confirmed=applications_confirmed,
            ),
            attendances_count=attendances_count,
            reviews_written_count=reviews_written_count,
        )
