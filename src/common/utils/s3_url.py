from src.common.config import settings
from src.common.constants import S3_PUBLIC_BUCKET_NAME


def get_public_image_url(file_key: str) -> str:
    endpoint = settings.S3_ENPOINT.rstrip("/")
    endpoint = endpoint.replace("/storage/v1/s3", "/storage/v1/object/public")
    return f"{endpoint}/{S3_PUBLIC_BUCKET_NAME}/{file_key}"


def convert_s3_url_to_public_url(s3_url: str) -> str:
    if "/storage/v1/s3/" in s3_url:
        return s3_url.replace("/storage/v1/s3/", "/storage/v1/object/public/")
    return s3_url

