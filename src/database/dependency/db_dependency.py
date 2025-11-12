from typing import Annotated, Generator

from fastapi import Depends
from sqlmodel import Session

from src.database.postgres.postgres_client import PostgresClient
from src.database.redis.redis_client import RedisClient
from src.database.s3.s3_client import S3Client

postgres_client = PostgresClient()
redis_client = RedisClient()
s3_client = S3Client()


def get_s3_client() -> S3Client:
    return s3_client


def get_redis_client() -> RedisClient:
    return redis_client


def get_db() -> Generator[Session, None, None]:
    yield from postgres_client.get_session()


S3ClientDep = Annotated[S3Client, Depends(get_s3_client)]
RedisClientDep = Annotated[RedisClient, Depends(get_redis_client)]
DatabaseDep = Annotated[Session, Depends(get_db)]
