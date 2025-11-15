from uuid import UUID

from sqlmodel import Session

from src.database.postgres.models.db_models import Application, Business, Market
from src.downstream.resend.resend_email_client import ResendEmailClient
from src.downstream.supabase.supabase_admin_client import SupabaseAdminClient


class ApplicationEmailService:
    def __init__(
        self, email_client: ResendEmailClient, supabase_client: SupabaseAdminClient
    ):
        self.email_client = email_client
        self.supabase_client = supabase_client

    def _get_vendor_email(
        self, owner_user_id: UUID, business_email: str | None = None
    ) -> str | None:
        user = self.supabase_client.get_user(owner_user_id)
        if user and user.email:
            return user.email
        return business_email

    def send_application_created_email(
        self, db: Session, application: Application
    ) -> None:
        market = db.get(Market, application.market_id)
        business = db.get(Business, application.business_id)

        if not market or not business:
            return

        vendor_email = self._get_vendor_email(business.owner_user_id, business.email)
        if not vendor_email:
            return

        subject = f"Application Submitted: {business.shop_name} applied to {market.market_name}"

        html_content = f"""
        <html>
        <body>
            <h2>Application Submitted Successfully</h2>
            <p>Your application has been submitted successfully!</p>
            <p><strong>Market:</strong> {market.market_name}</p>
            <p><strong>Business:</strong> {business.shop_name}</p>
            <p>You will be notified once the market organizer reviews your application.</p>
            <p>You can track the status of your application in your dashboard.</p>
        </body>
        </html>
        """

        self.email_client.send_email(
            to=vendor_email,
            subject=subject,
            html=html_content,
        )

    def send_application_accepted_email(
        self, db: Session, application: Application
    ) -> None:
        market = db.get(Market, application.market_id)
        business = db.get(Business, application.business_id)

        if not market or not business:
            return

        vendor_email = self._get_vendor_email(business.owner_user_id, business.email)
        if not vendor_email:
            return

        subject = f"Application Accepted: {business.shop_name} accepted to {market.market_name}"

        html_content = f"""
        <html>
        <body>
            <h2>Congratulations! Your Application Has Been Accepted</h2>
            <p>Great news! Your application has been accepted.</p>
            <p><strong>Market:</strong> {market.market_name}</p>
            <p><strong>Business:</strong> {business.shop_name}</p>
            <p>Next steps:</p>
            <ol>
                <li>Complete payment information in your application</li>
                <li>Confirm your participation</li>
            </ol>
            <p>You can manage your application in your dashboard.</p>
        </body>
        </html>
        """

        self.email_client.send_email(
            to=vendor_email,
            subject=subject,
            html=html_content,
        )

    def send_application_rejected_email(
        self, db: Session, application: Application
    ) -> None:
        market = db.get(Market, application.market_id)
        business = db.get(Business, application.business_id)

        if not market or not business:
            return

        vendor_email = self._get_vendor_email(business.owner_user_id, business.email)
        if not vendor_email:
            return

        subject = f"Application Update: {business.shop_name} - {market.market_name}"

        rejection_reason_text = (
            f"<p><strong>Reason:</strong> {application.rejection_reason}</p>"
            if application.rejection_reason
            else "<p>No specific reason was provided.</p>"
        )

        html_content = f"""
        <html>
        <body>
            <h2>Application Status Update</h2>
            <p>We regret to inform you that your application has been declined.</p>
            <p><strong>Market:</strong> {market.market_name}</p>
            <p><strong>Business:</strong> {business.shop_name}</p>
            {rejection_reason_text}
            <p>Thank you for your interest. We encourage you to apply to other markets.</p>
        </body>
        </html>
        """

        self.email_client.send_email(
            to=vendor_email,
            subject=subject,
            html=html_content,
        )

    def send_payment_updated_email(self, db: Session, application: Application) -> None:
        market = db.get(Market, application.market_id)
        business = db.get(Business, application.business_id)

        if not market or not business:
            return

        vendor_email = self._get_vendor_email(business.owner_user_id, business.email)
        if not vendor_email:
            return

        payment_method_text = (
            application.payment_method.value
            if application.payment_method
            else "Not set"
        )
        payment_status_text = (
            application.payment_status.value
            if application.payment_status
            else "Not set"
        )

        subject = (
            f"Payment Information Updated: {business.shop_name} - {market.market_name}"
        )

        html_content = f"""
        <html>
        <body>
            <h2>Payment Information Updated</h2>
            <p>The payment information for your application has been updated.</p>
            <p><strong>Market:</strong> {market.market_name}</p>
            <p><strong>Business:</strong> {business.shop_name}</p>
            <p><strong>Payment Method:</strong> {payment_method_text}</p>
            <p><strong>Payment Status:</strong> {payment_status_text}</p>
            <p>You can confirm your participation once you're ready.</p>
        </body>
        </html>
        """

        self.email_client.send_email(
            to=vendor_email,
            subject=subject,
            html=html_content,
        )

    def send_application_confirmed_email(
        self, db: Session, application: Application
    ) -> None:
        market = db.get(Market, application.market_id)
        business = db.get(Business, application.business_id)

        if not market or not business:
            return

        vendor_email = self._get_vendor_email(business.owner_user_id, business.email)
        if not vendor_email:
            return

        subject = f"Application Confirmed: {business.shop_name} confirmed for {market.market_name}"

        html_content = f"""
        <html>
        <body>
            <h2>Application Confirmed</h2>
            <p>Your application has been confirmed. You're all set!</p>
            <p><strong>Market:</strong> {market.market_name}</p>
            <p><strong>Business:</strong> {business.shop_name}</p>
            <p>We look forward to having you at the market!</p>
        </body>
        </html>
        """

        self.email_client.send_email(
            to=vendor_email,
            subject=subject,
            html=html_content,
        )

    def send_application_updated_email(
        self, db: Session, application: Application, changes: dict
    ) -> None:
        market = db.get(Market, application.market_id)
        business = db.get(Business, application.business_id)

        if not market or not business:
            return

        vendor_email = self._get_vendor_email(business.owner_user_id, business.email)
        if not vendor_email:
            return

        changes_list = []
        if "status" in changes:
            changes_list.append(f"Status: {changes['status']}")
        if "payment_method" in changes:
            changes_list.append(f"Payment Method: {changes['payment_method']}")
        if "payment_status" in changes:
            changes_list.append(f"Payment Status: {changes['payment_status']}")
        if "notes_for_org" in changes:
            changes_list.append("Notes updated")
        if "answers" in changes:
            changes_list.append("Application answers updated")

        if not changes_list:
            return

        subject = f"Application Updated: {business.shop_name} - {market.market_name}"

        changes_html = (
            "<ul>"
            + "".join([f"<li>{change}</li>" for change in changes_list])
            + "</ul>"
        )

        html_content = f"""
        <html>
        <body>
            <h2>Application Updated</h2>
            <p>Your application has been updated with the following changes:</p>
            {changes_html}
            <p><strong>Market:</strong> {market.market_name}</p>
            <p><strong>Business:</strong> {business.shop_name}</p>
            <p>You can view the updated details in your dashboard.</p>
        </body>
        </html>
        """

        self.email_client.send_email(
            to=vendor_email,
            subject=subject,
            html=html_content,
        )
