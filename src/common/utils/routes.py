from collections import defaultdict

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute

from src.common.logger import logger
from src.module.application.controller.application_controller import (
    router as application_router,
)
from src.module.auth.controller.auth_controller import router as auth_router
from src.module.business.controller.business_controller import router as business_router
from src.module.market.controller.market_controller import router as market_router
from src.module.review.controller.review_controller import router as review_router
from src.module.upload.controller.upload_controller import router as upload_router


def include_routers(app: FastAPI) -> None:
    app.include_router(auth_router)
    app.include_router(application_router)
    app.include_router(business_router)
    app.include_router(market_router)
    app.include_router(review_router)
    app.include_router(upload_router)

    api_router = APIRouter(prefix="/api", tags=["api"])
    app.include_router(api_router)

    log_routes(app)


def get_routes_by_module(app: FastAPI) -> dict[str, list[str]]:
    routes_by_module = defaultdict(list)

    for route in app.routes:
        if isinstance(route, APIRoute):
            route_string = f"{', '.join(route.methods)} {route.path}"

            path = route.path
            path_parts = [p for p in path.split("/") if p]

            if path_parts:
                module = path_parts[0]
            else:
                module = "root"

            routes_by_module[module].append(route_string)

    for module in routes_by_module:
        routes_by_module[module].sort()

    return dict(routes_by_module)


def log_routes(app: FastAPI) -> None:
    routes_by_module = get_routes_by_module(app)

    if not routes_by_module:
        logger.warning("No routes were found in the application")
        return

    logger.info("Mapped Routes:")

    for module in sorted(routes_by_module.keys()):
        logger.info(f"  [{module.upper()}]")
        for route in routes_by_module[module]:
            logger.info(f"    ▸ {route}")
