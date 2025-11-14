from typing import Annotated

from fastapi import Depends

from src.database.dependency.db_dependency import S3ClientDep
from src.database.s3.s3_client import S3Client
from src.module.upload.service.upload_service import UploadService


def get_upload_service(
    s3_client: S3ClientDep,
) -> UploadService:
    return UploadService(s3_client)


UploadServiceDep = Annotated[UploadService, Depends(get_upload_service)]

