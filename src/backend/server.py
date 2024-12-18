import secrets

from loguru import logger
from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.concurrency import asynccontextmanager
from apscheduler.triggers.cron import CronTrigger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.env import ENV
from backend.views.log_view import get_projects_with_recent_logs
from backend.controllers.log_controller import log_router
from backend.controllers.task_controller import task_router
from backend.controllers.user_controller import user_router
from backend.controllers.project_controller import project_router
from backend.controllers.dashboard_controller import dashboard_router
from backend.controllers.healthcheck_controller import healthcheck_router

scheduler = AsyncIOScheduler()

async def scheduled_get_projects_with_recent_logs():
    try:
        await get_projects_with_recent_logs()
        logger.info("Emails send to clients successfully.")
    except Exception as e:
        logger.error(f"Error running scheduled task: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Configure the trigger for daily at 11:59 PM
    trigger = CronTrigger(hour=23, minute=57)

    # Add the asynchronous job to the scheduler
    scheduler.add_job(
        scheduled_get_projects_with_recent_logs,
        trigger,
        id="daily_project_log_job",
        name="Daily Project Logs Retrieval and Email Sending",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("APScheduler started and job added.")

    yield

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


class AuthRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_paths = [
            "/user/login",
            "/healthcheck",
        ]

        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        user_id = request.session.get("user_id")
        if not user_id:
            return RedirectResponse(url="/user/login")

        response = await call_next(request)
        return response


app.add_middleware(AuthRedirectMiddleware)
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
app.include_router(log_router, tags=["Log"])
app.include_router(dashboard_router, tags=["Dashboard"])
