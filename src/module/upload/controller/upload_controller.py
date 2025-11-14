from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from src.common.logger import logger
from src.common.utils.response import Response, StandardResponse, Status
from src.database.dependency.db_dependency import DatabaseDep
from src.module.auth.dependency.auth_dependency import get_current_user
from src.module.upload.dependency.upload_dependency import UploadServiceDep

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/image", status_code=Status.CREATED)
async def upload_image(
    file: UploadFile = File(...),
    entity_type: Annotated[
        str, Query(description="Entity type (e.g., 'market', 'business')")
    ] = "market",
    current_user: Annotated[UUID, Depends(get_current_user)] = None,
    upload_service: UploadServiceDep = None,
    db: DatabaseDep = None,
) -> StandardResponse:
    logger.info(
        f"Uploading single image for {entity_type} entity by user {current_user}"
    )
    try:
        result = await upload_service.upload_single_image(
            file, entity_type, current_user, db
        )
        return Response.success(
            message="Image uploaded successfully",
            data=result.model_dump(),
            status_code=Status.CREATED,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")


@router.post("/images", status_code=Status.CREATED)
async def upload_images(
    files: list[UploadFile] = File(...),
    entity_type: Annotated[
        str, Query(description="Entity type (e.g., 'market', 'business')")
    ] = "market",
    current_user: Annotated[UUID, Depends(get_current_user)] = None,
    upload_service: UploadServiceDep = None,
    db: DatabaseDep = None,
) -> StandardResponse:
    logger.info(
        f"Uploading {len(files)} images for {entity_type} entity by user {current_user}"
    )
    try:
        result = await upload_service.upload_multiple_images(
            files, entity_type, current_user, db
        )
        return Response.success(
            message=f"Successfully uploaded {len(result.images)} image(s)",
            data=result.model_dump(),
            status_code=Status.CREATED,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload images: {str(e)}",
        )
