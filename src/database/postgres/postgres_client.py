from typing import Generator

from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine

from src.common.config import settings
from src.database.postgres.models.db_models import Resume  # noqa


class PostgresClient:
    def __init__(self):
        self.database_url = settings.POSTGRES_URL
        self.engine = self._create_engine()

    def _create_engine(self):
        try:
            return create_engine(self.database_url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    def get_session(self) -> Generator[Session, None, None]:
        try:
            with Session(self.engine) as session:
                yield session
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    def create_tables(self):
        try:
            SQLModel.metadata.create_all(self.engine)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")
