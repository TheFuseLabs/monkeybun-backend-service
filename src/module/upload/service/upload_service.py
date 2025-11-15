from typing import Optional
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlmodel import Session

from src.common.constants import S3_PUBLIC_BUCKET_NAME
from src.common.utils.s3_url import get_public_image_url
from src.database.postgres.models.db_models import PendingImage
from src.database.s3.s3_client import S3Client
from src.module.upload.schema.upload_schema import (
    BatchImageUploadResponse,
    ImageUploadResponse,
)


class UploadService:
    def __init__(self, s3_client: S3Client):
        self.s3_client = s3_client
        self.allowed_content_types = ["image/jpeg", "image/jpg", "image/png"]
        self.allowed_extensions = ["jpg", "jpeg", "png"]

    def _validate_image_file(self, file, filename: Optional[str] = None) -> str:
        if (
            not file.content_type
            or file.content_type.lower() not in self.allowed_content_types
        ):
            raise HTTPException(
                status_code=400,
                detail=f"File {filename or 'unknown'}: Only JPEG and PNG images are allowed",
            )

        file_extension = (
            filename.split(".")[-1].lower() if filename and "." in filename else None
        )
        if not file_extension or file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File {filename or 'unknown'}: Must have a .jpg, .jpeg, or .png extension",
            )

        return file_extension

    async def upload_single_image(
        self,
        file,
        entity_type: str,
        user_id: UUID,
        db: Session,
    ) -> ImageUploadResponse:
        self._validate_image_file(file, file.filename)

        file_extension = (
            file.filename.split(".")[-1].lower() if "." in file.filename else "jpg"
        )
        file_key = f"{entity_type}/{uuid4()}.{file_extension}"

        await self.s3_client.upload_file(
            file.file,
            file_key,
            content_type=file.content_type,
            bucket_name=S3_PUBLIC_BUCKET_NAME,
        )

        image_url = get_public_image_url(file_key)

        pending_image = PendingImage(
            user_id=user_id, image_url=image_url, s3_key=file_key
        )
        db.add(pending_image)
        db.commit()

        return ImageUploadResponse(url=image_url, key=file_key)

    async def upload_multiple_images(
        self,
        files: list,
        entity_type: str,
        user_id: UUID,
        db: Session,
        max_files: int = 20,
    ) -> BatchImageUploadResponse:
        if not files:
            raise HTTPException(status_code=400, detail="At least one file is required")

        if len(files) > max_files:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {max_files} images can be uploaded at once",
            )

        uploaded_images = []

        try:
            for file in files:
                self._validate_image_file(file, file.filename)

                file_extension = (
                    file.filename.split(".")[-1].lower()
                    if "." in file.filename
                    else "jpg"
                )
                file_key = f"{entity_type}/{uuid4()}.{file_extension}"

                await self.s3_client.upload_file(
                    file.file,
                    file_key,
                    content_type=file.content_type,
                    bucket_name=S3_PUBLIC_BUCKET_NAME,
                )

                image_url = get_public_image_url(file_key)

                pending_image = PendingImage(
                    user_id=user_id, image_url=image_url, s3_key=file_key
                )
                db.add(pending_image)

                uploaded_images.append(ImageUploadResponse(url=image_url, key=file_key))

            db.commit()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload images: {str(e)}",
            )

        return BatchImageUploadResponse(images=uploaded_images)
