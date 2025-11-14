from typing import Annotated, Generator

from fastapi import Depends
from sqlmodel import Session

from src.database.postgres.postgres_client import PostgresClient
from src.database.s3.s3_client import S3Client

postgres_client = PostgresClient()
s3_client = S3Client()


def get_s3_client() -> S3Client:
    return s3_client


def get_db() -> Generator[Session, None, None]:
    yield from postgres_client.get_session()


S3ClientDep = Annotated[S3Client, Depends(get_s3_client)]
DatabaseDep = Annotated[Session, Depends(get_db)]
