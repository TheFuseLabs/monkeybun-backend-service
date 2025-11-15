from src.downstream.resend.resend_email_client import ResendEmailClient

resend_email_client = ResendEmailClient()


def get_resend_email_client() -> ResendEmailClient:
    return resend_email_client

