from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    url: str
    key: str


class BatchImageUploadResponse(BaseModel):
    images: list[ImageUploadResponse]
