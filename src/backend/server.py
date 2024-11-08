from typing import Callable

from loguru import logger
from fastapi import FastAPI, Request, Response
from starlette.middleware.cors import CORSMiddleware

from src.config.env import ENV
from backend.controllers.user_controller import user_router
from src.backend.controllers.healthcheck_controller import healthcheck_router

app = FastAPI(title="Divison5 Reports API", version="0.1.0")

origins = [ENV.API_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_request(request: Request, call_next: Callable):
    logger.debug(
        f"Request: {request.method} {request.url} Headers: {request.headers}"
    )
    response: Response = await call_next(request)
    return response


app.include_router(healthcheck_router, tags=["Health Check"])
app.include_router(user_router, prefix="/v1", tags=["Auth"])
