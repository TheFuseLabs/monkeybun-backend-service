from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.common.constants import PROJECT_TITLE
from src.common.logger import logger, setup_logging
from src.common.utils.exception_handlers import register_exception_handlers
from src.common.utils.response import Response
from src.common.utils.routes import include_routers


def create_app() -> FastAPI:
    setup_logging()

    app: FastAPI = FastAPI(
        title=PROJECT_TITLE,
        servers=[
            {
                "url": "http://127.0.0.1:8000",
                "description": "Local Development Server",
            },
        ],
        summary="Monkeybun Backend Service API",
        description="Monkeybun Backend Service API",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    include_routers(app)
    register_exception_handlers(app)

    return app


# ========== FAST API APPLICATION ==========
app: FastAPI = create_app()


# ========== HEALTH CHECK ROUTES ==========
@app.get("/")
@app.get("/health")
@app.get("/healthz")
async def health_check() -> JSONResponse:
    logger.info("Server is Healthy")
    return Response.success(message="Server is Healthy")
