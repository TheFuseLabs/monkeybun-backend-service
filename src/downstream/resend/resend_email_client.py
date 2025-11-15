from typing import Optional

import resend

from src.common.config import settings
from src.common.logger import logger


class ResendEmailClient:
    def __init__(self):
        if settings.RESEND_ENABLED:
            resend.api_key = settings.RESEND_API_KEY
        self.from_email = settings.RESEND_FROM_EMAIL
        self.from_name = settings.RESEND_FROM_NAME

    def send_email(
        self,
        to: str | list[str],
        subject: str,
        html: Optional[str] = None,
        text: Optional[str] = None,
    ) -> dict:
        if not settings.RESEND_ENABLED:
            logger.info(
                f"Email sending is disabled. Would have sent email to {to} with subject: {subject}"
            )
            return {"id": "disabled", "message": "Email sending is disabled"}

        try:
            from_address = f"{self.from_name} <{self.from_email}>"
            params = resend.Emails.SendParams(
                {
                    "from": from_address,
                    "to": to if isinstance(to, list) else [to],
                    "subject": subject,
                }
            )

            if html:
                params["html"] = html
            if text:
                params["text"] = text

            response = resend.Emails.send(params)
            logger.info(f"Email sent successfully to {to}: {response}")
            return response
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {str(e)}")
            raise
