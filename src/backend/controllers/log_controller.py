from typing import Optional
from datetime import datetime

from ulid import ULID
from fastapi import Form, Depends, Query, Request, APIRouter, HTTPException
from sqlalchemy import asc, desc
from fastapi.responses import HTMLResponse, RedirectResponse

from backend.models import LogCreateModel, LogResponseModel
from core.models.log import Log
from database.models import log_mapper  # noqa F401
from core.models.user import User
from backend.dependencies import get_session
from backend.views.log_view import (
    get_log,
    create_log,
    update_log,
    upsert_log,
    get_all_logs,
)
from backend.utils.templates import templates
from backend.views.user_view import get_user_logs
from backend.dependencies.auth import (
    is_admin,
    validate_csrf,
    get_current_user,
)
from backend.models.pagination import Pagination
from database.interfaces.session import ISession

log_router = APIRouter(prefix="/log")


@log_router.get("/create", response_class=HTMLResponse)
def get_log_home(
    request: Request,
    task_id: Optional[str] = Query(None),
    task_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse("log/create.html", {"request": request, "task_id": task_id, "task_name": task_name})


@log_router.post("/", response_class=HTMLResponse)
async def create_log_endpoint(
    request: Request,
    task_name: str = Form(...),
    description: str = Form(...),
    hours_spent_today: float = Form(...),
    task_status: str = Form(...),
    task_id: str = Form(...),
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    csrf_protect=Depends(validate_csrf),
):
    log_data = LogCreateModel(
        id=str(ULID()),
        task_name=task_name,
        description=description,
        hours_spent_today=hours_spent_today,
        task_status=task_status,
        user_id=current_user.id,
        timestamp=int(datetime.now().timestamp()),
        task_id=task_id,
    )
    try:
        log = create_log(log_data, session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return RedirectResponse(f"/log/{log.id}", status_code=303)


@log_router.get("/{log_id}", response_class=HTMLResponse)
def get_log_endpoint(
    request: Request,
    log_id: str,
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    try:
        log = get_log(session, id=log_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return templates.TemplateResponse(
        "log/detail.html", {"request": request, "log": log}
    )


@log_router.put("/{log_id}", response_model=LogResponseModel)
def update_log_endpoint(
    log_id: str,
    log_update: LogCreateModel,
    session: ISession = Depends(get_session),
):
    try:
        log = update_log(log_id, log_update, session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return log


@log_router.post("/upsert", response_model=LogResponseModel)
def upsert_log_endpoint(
    log: LogResponseModel, session: ISession = Depends(get_session)
):
    try:
        log = upsert_log(log, session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return log


@log_router.get("/", response_class=HTMLResponse)
def get_all_logs_endpoint(
    request: Request,
    page: int = 1,
    sort: Optional[str] = None,
    order: Optional[str] = None,
    limit: int = 15,
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    order_by = []

    sort_mapping = {
        "Task Name": "task_name",
        "Hours Spent Today": "hours_spent_today",
        "Task Status": "task_status",
        "Timestamp": "timestamp",
    }

    if sort:
        sort_field = sort_mapping.get(sort)
        if sort_field:
            sort_column = getattr(Log, sort_field, None)
            if sort_column:
                if order and order.lower() == "desc":
                    order_by.append(desc(sort_column))
                else:
                    order_by.append(asc(sort_column))

    pagination = Pagination(limit=limit, current_page=page, order_by=order_by)

    if is_admin(current_user):
        logs, pagination = get_all_logs(session, pagination)
    else:
        logs, pagination = get_user_logs(session, current_user.id, pagination)

    table_headers = [
        "Task Name",
        "Hours Spent Today",
        "Description",
        "Timestamp",
        "Task Status",
    ]

    return templates.TemplateResponse(
        "log/logs.html",
        {
            "request": request,
            "headers": table_headers,
            "data": logs,
            "pagination": pagination,
            "entity": "log",
            "current_sort": sort,
            "current_order": order,
        },
    )
