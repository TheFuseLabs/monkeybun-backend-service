from typing import BinaryIO, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException

from src.common.config import settings
from src.common.constants import S3_PUBLIC_BUCKET_NAME
from src.common.logger import logger


class S3Client:
    def __init__(self):
        self.s3_client = self._create_s3_client()

    def _create_s3_client(self):
        try:
            s3_client = boto3.client(
                "s3",
                endpoint_url=settings.S3_ENDPOINT,
                region_name=settings.S3_REGION,
                aws_access_key_id=settings.S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY_ID,
            )
            return s3_client
        except NoCredentialsError:
            raise HTTPException(
                status_code=500,
                detail="Supabase S3 credentials not found. Please configure your Supabase credentials.",
            )

    async def upload_file(
        self,
        file: BinaryIO,
        file_key: str,
        content_type: Optional[str] = None,
        bucket_name: Optional[str] = None,
    ) -> str:
        try:
            file.seek(0)
            file_content = file.read()

            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type

            bucket = bucket_name or S3_PUBLIC_BUCKET_NAME
            self.s3_client.put_object(
                Bucket=bucket, Key=file_key, Body=file_content, **extra_args
            )

            return f"File uploaded successfully: {file_key}"
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchBucket":
                bucket = bucket_name or S3_PUBLIC_BUCKET_NAME
                raise HTTPException(
                    status_code=404, detail=f"Bucket not found: {bucket}"
                )
            raise HTTPException(
                status_code=500, detail=f"Failed to upload file: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to upload file: {str(e)}"
            )

    async def delete_file(
        self, file_key: str, bucket_name: Optional[str] = None
    ) -> str:
        try:
            bucket = bucket_name or S3_PUBLIC_BUCKET_NAME
            self.s3_client.delete_object(Bucket=bucket, Key=file_key)

            return f"File deleted successfully: {file_key}"
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchBucket":
                bucket = bucket_name or S3_PUBLIC_BUCKET_NAME
                raise HTTPException(
                    status_code=404, detail=f"Bucket not found: {bucket}"
                )
            elif error_code == "NoSuchKey":
                raise HTTPException(
                    status_code=404, detail=f"File not found: {file_key}"
                )
            raise HTTPException(
                status_code=500, detail=f"Failed to delete file: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete file: {str(e)}"
            )

    async def update_file(
        self,
        file: BinaryIO,
        file_key: str,
        content_type: Optional[str] = None,
        bucket_name: Optional[str] = None,
    ) -> str:
        try:
            bucket = bucket_name or S3_PUBLIC_BUCKET_NAME
            await self.delete_file(file_key, bucket)
            await self.upload_file(file, file_key, content_type, bucket)
            return f"File updated successfully: {file_key}"
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to update file: {str(e)}"
            )

    def download_file_sync(
        self, file_key: str, bucket_name: Optional[str] = None
    ) -> bytes:
        try:
            logger.debug(f"Downloading file from bucket: {bucket_name or 'default'}")
            bucket = bucket_name or S3_PUBLIC_BUCKET_NAME
            response = self.s3_client.get_object(Bucket=bucket, Key=file_key)

            return response["Body"].read()
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchBucket":
                bucket = bucket_name or S3_PUBLIC_BUCKET_NAME
                raise HTTPException(
                    status_code=404, detail=f"Bucket not found: {bucket}"
                )
            elif error_code == "NoSuchKey":
                raise HTTPException(
                    status_code=404, detail=f"File not found: {file_key}"
                )
            raise HTTPException(
                status_code=500, detail=f"Failed to download file: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to download file: {str(e)}"
            )

    async def download_file(
        self, file_key: str, bucket_name: Optional[str] = None
    ) -> bytes:
        try:
            logger.debug(f"Downloading file from bucket: {bucket_name or 'default'}")
            bucket = bucket_name or S3_PUBLIC_BUCKET_NAME
            response = self.s3_client.get_object(Bucket=bucket, Key=file_key)

            return response["Body"].read()
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchBucket":
                bucket = bucket_name or S3_PUBLIC_BUCKET_NAME
                raise HTTPException(
                    status_code=404, detail=f"Bucket not found: {bucket}"
                )
            elif error_code == "NoSuchKey":
                raise HTTPException(
                    status_code=404, detail=f"File not found: {file_key}"
                )
            raise HTTPException(
                status_code=500, detail=f"Failed to download file: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to download file: {str(e)}"
            )

    async def file_exists(
        self, file_key: str, bucket_name: Optional[str] = None
    ) -> bool:
        try:
            bucket = bucket_name or S3_PUBLIC_BUCKET_NAME
            self.s3_client.head_object(Bucket=bucket, Key=file_key)
            return True
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchBucket":
                bucket = bucket_name or S3_PUBLIC_BUCKET_NAME
                raise HTTPException(
                    status_code=404, detail=f"Bucket not found: {bucket}"
                )
            elif error_code == "404":
                return False
            raise HTTPException(
                status_code=500, detail=f"Failed to check file existence: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to check file existence: {str(e)}"
            )
