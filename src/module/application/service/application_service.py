from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, func
from sqlmodel import Session, select

from src.database.postgres.models.db_models import (
    Application,
    ApplicationStatus,
    Business,
    Market,
)
from src.module.application.schema.application_schema import (
    ApplicationAcceptRequest,
    ApplicationConfirmRequest,
    ApplicationCreateRequest,
    ApplicationListResponse,
    ApplicationPaymentUpdateRequest,
    ApplicationRejectRequest,
    ApplicationResponse,
    ApplicationSearchFilters,
    ApplicationSearchResponse,
    ApplicationUpdateRequest,
)
from src.module.application.service.email_service import ApplicationEmailService


class ApplicationService:
    def __init__(self, email_service: ApplicationEmailService | None = None):
        self.email_service = email_service

    def create_application(
        self, db: Session, user_id: UUID, request: ApplicationCreateRequest
    ) -> ApplicationResponse:
        market = db.get(Market, request.market_id)
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")

        business = db.get(Business, request.business_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        if business.owner_user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to create applications for this business",
            )

        existing_application = db.exec(
            select(Application).where(
                and_(
                    Application.market_id == request.market_id,
                    Application.business_id == request.business_id,
                )
            )
        ).first()

        if existing_application:
            raise HTTPException(
                status_code=400,
                detail="A business cannot apply to the same market twice. An application already exists for this business and market.",
            )

        if request.answers and market.application_form:
            self._validate_answers(request.answers, market.application_form)

        application = Application(
            market_id=request.market_id,
            business_id=request.business_id,
            status=ApplicationStatus.applied,
            answers=request.answers,
        )
        db.add(application)

        try:
            db.commit()
            db.refresh(application)
        except Exception as e:
            db.rollback()
            error_str = str(e).lower()
            if (
                "unique" in error_str
                or "duplicate" in error_str
                or "applications_market_id_business_id_key" in error_str
            ):
                raise HTTPException(
                    status_code=400,
                    detail="A business cannot apply to the same market twice. An application already exists for this business and market.",
                )
            raise

        if self.email_service:
            try:
                self.email_service.send_application_created_email(db, application)
            except Exception as e:
                from src.common.logger import logger

                logger.error(f"Failed to send application created email: {str(e)}")

        return ApplicationResponse.model_validate(application.model_dump())

    def get_application_by_id(
        self, db: Session, application_id: UUID
    ) -> ApplicationResponse:
        application = db.get(Application, application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        return ApplicationResponse.model_validate(application.model_dump())

    def search_applications(
        self, db: Session, filters: ApplicationSearchFilters
    ) -> ApplicationListResponse:
        query = select(Application)

        conditions = []

        if filters.market_id:
            conditions.append(Application.market_id == filters.market_id)

        if filters.business_id:
            conditions.append(Application.business_id == filters.business_id)

        if filters.status:
            conditions.append(Application.status == filters.status)

        if conditions:
            query = query.where(and_(*conditions))

        total_query = select(func.count()).select_from(Application)
        if conditions:
            total_query = total_query.where(and_(*conditions))

        total = db.exec(total_query).one()

        query = query.order_by(Application.created_at.desc())
        query = query.offset(filters.offset).limit(filters.limit)

        applications = db.exec(query).all()

        application_responses = []
        for application in applications:
            application_responses.append(
                ApplicationSearchResponse(
                    id=application.id,
                    market_id=application.market_id,
                    business_id=application.business_id,
                    status=application.status,
                    applied_at=application.applied_at,
                    rejection_reason=application.rejection_reason,
                    created_at=application.created_at,
                )
            )

        return ApplicationListResponse(
            applications=application_responses,
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )

    def update_application(
        self,
        db: Session,
        application_id: UUID,
        user_id: UUID,
        request: ApplicationUpdateRequest,
    ) -> ApplicationResponse:
        application = db.get(Application, application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        business = db.get(Business, application.business_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        if business.owner_user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to update this application",
            )

        update_data = request.model_dump(exclude_unset=True)

        old_status = application.status
        new_status = update_data.get("status")

        if new_status and new_status != old_status:
            self._update_status_timestamps(application, new_status)

        if "answers" in update_data and update_data["answers"]:
            market = db.get(Market, application.market_id)
            if market and market.application_form:
                self._validate_answers(update_data["answers"], market.application_form)

        changes = {}
        for key, value in update_data.items():
            old_value = getattr(application, key, None)
            setattr(application, key, value)
            if old_value != value:
                if key == "status" and value:
                    changes[key] = (
                        value.value if hasattr(value, "value") else str(value)
                    )
                elif key == "payment_method" and value:
                    changes[key] = (
                        value.value if hasattr(value, "value") else str(value)
                    )
                elif key == "payment_status" and value:
                    changes[key] = (
                        value.value if hasattr(value, "value") else str(value)
                    )
                elif key in ["notes_for_org", "answers"]:
                    changes[key] = "updated"

        db.add(application)
        db.commit()
        db.refresh(application)

        if self.email_service and changes:
            try:
                self.email_service.send_application_updated_email(
                    db, application, changes
                )
            except Exception as e:
                from src.common.logger import logger

                logger.error(f"Failed to send application updated email: {str(e)}")

        return ApplicationResponse.model_validate(application.model_dump())

    def delete_application(
        self, db: Session, application_id: UUID, user_id: UUID
    ) -> None:
        application = db.get(Application, application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        business = db.get(Business, application.business_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        if business.owner_user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to delete this application",
            )

        db.delete(application)
        db.commit()

    def accept_application(
        self,
        db: Session,
        application_id: UUID,
        user_id: UUID,
        request: ApplicationAcceptRequest,
    ) -> ApplicationResponse:
        application = db.get(Application, application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        market = db.get(Market, application.market_id)
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")

        if market.organizer_user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to accept applications for this market",
            )

        if application.status == ApplicationStatus.accepted:
            raise HTTPException(
                status_code=400,
                detail="Application is already accepted",
            )

        application.status = ApplicationStatus.accepted
        self._update_status_timestamps(application, ApplicationStatus.accepted)
        application.rejection_reason = None

        db.add(application)
        db.commit()
        db.refresh(application)

        if self.email_service:
            try:
                self.email_service.send_application_accepted_email(db, application)
            except Exception as e:
                from src.common.logger import logger

                logger.error(f"Failed to send application accepted email: {str(e)}")

        return ApplicationResponse.model_validate(application.model_dump())

    def reject_application(
        self,
        db: Session,
        application_id: UUID,
        user_id: UUID,
        request: ApplicationRejectRequest,
    ) -> ApplicationResponse:
        application = db.get(Application, application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        market = db.get(Market, application.market_id)
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")

        if market.organizer_user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to reject applications for this market",
            )

        if application.status == ApplicationStatus.declined:
            raise HTTPException(
                status_code=400,
                detail="Application is already declined",
            )

        application.status = ApplicationStatus.declined
        self._update_status_timestamps(application, ApplicationStatus.declined)
        application.rejection_reason = request.rejection_reason

        db.add(application)
        db.commit()
        db.refresh(application)

        if self.email_service:
            try:
                self.email_service.send_application_rejected_email(db, application)
            except Exception as e:
                from src.common.logger import logger

                logger.error(f"Failed to send application rejected email: {str(e)}")

        return ApplicationResponse.model_validate(application.model_dump())

    def get_my_applications(
        self,
        db: Session,
        user_id: UUID,
        status: ApplicationStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> ApplicationListResponse:
        user_businesses = db.exec(
            select(Business).where(Business.owner_user_id == user_id)
        ).all()

        if not user_businesses:
            return ApplicationListResponse(
                applications=[],
                total=0,
                limit=limit,
                offset=offset,
            )

        business_ids = [business.id for business in user_businesses]

        conditions = [Application.business_id.in_(business_ids)]

        if status:
            conditions.append(Application.status == status)

        query = select(Application)
        if conditions:
            query = query.where(and_(*conditions))

        total_query = select(func.count()).select_from(Application)
        if conditions:
            total_query = total_query.where(and_(*conditions))

        total = db.exec(total_query).one()

        query = query.order_by(Application.created_at.desc())
        query = query.offset(offset).limit(limit)

        applications = db.exec(query).all()

        application_responses = []
        for application in applications:
            application_responses.append(
                ApplicationSearchResponse(
                    id=application.id,
                    market_id=application.market_id,
                    business_id=application.business_id,
                    status=application.status,
                    applied_at=application.applied_at,
                    rejection_reason=application.rejection_reason,
                    created_at=application.created_at,
                )
            )

        return ApplicationListResponse(
            applications=application_responses,
            total=total,
            limit=limit,
            offset=offset,
        )

    def update_payment(
        self,
        db: Session,
        application_id: UUID,
        user_id: UUID,
        request: ApplicationPaymentUpdateRequest,
    ) -> ApplicationResponse:
        application = db.get(Application, application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        business = db.get(Business, application.business_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        if business.owner_user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to update payment for this application",
            )

        if application.status != ApplicationStatus.accepted:
            raise HTTPException(
                status_code=400,
                detail="Payment can only be updated for accepted applications",
            )

        update_data = request.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(application, key, value)

        db.add(application)
        db.commit()
        db.refresh(application)

        if self.email_service:
            try:
                self.email_service.send_payment_updated_email(db, application)
            except Exception as e:
                from src.common.logger import logger

                logger.error(f"Failed to send payment updated email: {str(e)}")

        return ApplicationResponse.model_validate(application.model_dump())

    def confirm_application(
        self,
        db: Session,
        application_id: UUID,
        user_id: UUID,
        request: ApplicationConfirmRequest,
    ) -> ApplicationResponse:
        application = db.get(Application, application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        business = db.get(Business, application.business_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        if business.owner_user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to confirm this application",
            )

        if application.status == ApplicationStatus.confirmed:
            raise HTTPException(
                status_code=400,
                detail="Application is already confirmed",
            )

        if application.status != ApplicationStatus.accepted:
            raise HTTPException(
                status_code=400,
                detail="Only accepted applications can be confirmed",
            )

        application.status = ApplicationStatus.confirmed
        self._update_status_timestamps(application, ApplicationStatus.confirmed)

        db.add(application)
        db.commit()
        db.refresh(application)

        if self.email_service:
            try:
                self.email_service.send_application_confirmed_email(db, application)
            except Exception as e:
                from src.common.logger import logger

                logger.error(f"Failed to send application confirmed email: {str(e)}")

        return ApplicationResponse.model_validate(application.model_dump())

    def _update_status_timestamps(
        self, application: Application, new_status: ApplicationStatus
    ) -> None:
        now = datetime.now(timezone.utc)

        if new_status == ApplicationStatus.accepted:
            if not application.accepted_at:
                application.accepted_at = now
        elif new_status == ApplicationStatus.declined:
            if not application.declined_at:
                application.declined_at = now
        elif new_status == ApplicationStatus.confirmed:
            if not application.confirmed_at:
                application.confirmed_at = now

    def _validate_answers(self, answers: dict, application_form: dict) -> None:
        if not isinstance(application_form, dict):
            return

        questions = application_form.get("questions", [])
        if not isinstance(questions, list):
            return

        question_map = {
            q.get("id"): q for q in questions if isinstance(q, dict) and "id" in q
        }

        for question_id, question in question_map.items():
            if question.get("required", False):
                if question_id not in answers or answers[question_id] is None:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Required question '{question_id}' is missing an answer",
                    )

            if question_id in answers:
                answer = answers[question_id]
                question_type = question.get("type")

                if question_type == "single_choice":
                    options = question.get("options", [])
                    if answer not in options:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Answer for '{question_id}' must be one of the provided options",
                        )
                elif question_type == "multiple_choice":
                    options = question.get("options", [])
                    if not isinstance(answer, list):
                        raise HTTPException(
                            status_code=400,
                            detail=f"Answer for '{question_id}' must be a list",
                        )
                    if not all(item in options for item in answer):
                        raise HTTPException(
                            status_code=400,
                            detail=f"All answers for '{question_id}' must be from the provided options",
                        )
