import secrets

from loguru import logger
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.config.env import ENV
from src.backend.controllers.task_controller import task_router
from src.backend.controllers.user_controller import user_router
from src.backend.controllers.project_controller import project_router
from src.backend.controllers.dashboard_controller import dashboard_router
from src.backend.controllers.healthcheck_controller import healthcheck_router

app = FastAPI(title="Division5 Reports API", version="0.1.0")


class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.debug(
            f"Request: {request.method} {request.url} Headers: {request.headers}"
        )
        response: Response = await call_next(request)
        return response


app.add_middleware(LogRequestMiddleware)


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "csrftoken" not in request.session:
            request.session["csrftoken"] = secrets.token_hex(32)
        response = await call_next(request)
        return response


app.add_middleware(CSRFMiddleware)

app.add_middleware(
    SessionMiddleware,
    secret_key=ENV.SECRET_KEY,
    max_age=60 * 60 * 24 * 365 * 10,
    same_site="lax",
    https_only=ENV.ENV == "prod",
)

origins = [ENV.API_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(healthcheck_router, tags=["Health Check"])
app.include_router(user_router, tags=["User"])
app.include_router(project_router, tags=["Project"])
app.include_router(task_router, tags=["Task"])
app.include_router(dashboard_router, tags=["Dashboard"])
