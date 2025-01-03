from io import StringIO
import csv
from typing import Optional
from datetime import datetime

from ulid import ULID
from loguru import logger
from fastapi import (
    Form,
    Query,
    Depends,
    Request,
    Response,
    APIRouter,
    HTTPException,
)
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse

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
from backend.utils.filters_and_sort import get_filters, get_sorting
from database.interfaces.session import ISession

log_router = APIRouter(prefix="/log")


@log_router.get("/create", response_class=HTMLResponse)
def get_log_home(
    request: Request,
    task_id: Optional[str] = Query(None),
    task_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        "log/create.html",
        {"request": request, "task_id": task_id, "task_name": task_name},
    )


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
    log_id = str(ULID())
    log_data = LogCreateModel(
        id=log_id,
        task_name=task_name,
        description=description,
        hours_spent_today=hours_spent_today,
        task_status=task_status,
        user_id=current_user.id,
        user_name=current_user.full_name,
        timestamp=int(datetime.now().timestamp()),
        task_id=task_id,
    )
    try:
        create_log(log_data, session)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail=str(e))
    return RedirectResponse(f"/log/{log_id}", status_code=303)


@log_router.get("/export", response_class=StreamingResponse)
def export_tasks_csv(
    request: Request,
    combined_filters: Optional[str] = Query(None),
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Export tasks between two dates as a CSV file.
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Access forbidden")
    try:
        filter_mapping = {
            "Date": "timestamp",
            "Task Name": "task_name",
            "Hours Worked": "hours_spent_today",
            "User": "user_name",
            "Description": "description",
            "Task Status": "task_status",
        }
        pagination = Pagination(limit=None, current_page=1, order_by=[])
        filters = get_filters(
            combined_filters,
            filter_mapping,
            "Task Name",
            date_fields=["Date"],
        )

        logs, _ = get_all_logs(
            session,
            pagination,
            **filters,
        )
        csv_file = StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "ID",
                "Task Name",
                "User",
                "Task Status",
                "Hours Spent",
                "Date",
            ]
        )
        for log in logs:
            writer.writerow(
                [
                    log.id,
                    log.task_name,
                    log.user_name,
                    log.task_status,
                    log.hours_spent_today,
                    datetime.fromtimestamp(log.timestamp).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                ]
            )
        csv_file.seek(0)
        response = StreamingResponse(
            iter([csv_file.getvalue()]),
            media_type="text/csv",
        )
        response.headers["Content-Disposition"] = (
            "attachment; filename=logs.csv"
        )
        return response
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Error exporting tasks")


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


@log_router.get("/{log_id}/edit", response_model=LogResponseModel)
def update_project_page(
    Request: Request,
    log_id: str,
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    log = get_log(session, id=log_id)

    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    return templates.TemplateResponse(
        "log/edit.html",
        {
            "log": log,
            "request": Request,
            "current_time": datetime.now().timestamp(),
        },
    )


@log_router.put("/{log_id}", response_class=HTMLResponse)
async def update_log_endpoint(
    request: Request,
    log_id: str,
    task_name: str = Form(...),
    description: str = Form(...),
    hours_spent_today: float = Form(...),
    task_status: str = Form(...),
    task_id: str = Form(...),
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    log_update = LogCreateModel(
        id=log_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        task_name=task_name,
        description=description,
        hours_spent_today=hours_spent_today,
        task_status=task_status,
        task_id=task_id,
    )

    update_log(log_id, log_update, session)

    headers = {"HX-Redirect": f"/log/{log_id}"}
    return Response(status_code=200, headers=headers)


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
    sort: Optional[str] = "Date",
    order: Optional[str] = "desc",
    limit: int = 15,
    combined_filters: Optional[str] = Query(None),
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    sort_mapping = {
        "ID": Log.id,
        "Task Name": Log.task_name,
        "Hours ": Log.hours_spent_today,
        "Task Status": Log.task_status,
        "Date": Log.timestamp,
    }

    order_by = get_sorting(sort, order, sort_mapping)
    pagination = Pagination(limit=limit, current_page=page, order_by=order_by)

    filter_mapping = {
        "Date": "timestamp",
        "Task Name": "task_name",
        "Hours Worked": "hours_spent_today",
        "User": "user_name",
        "Description": "description",
        "Task Status": "task_status",
    }

    filters = get_filters(combined_filters, filter_mapping, "Task Name", date_fields=["Date"])

    if is_admin(current_user):
        logs, pagination = get_all_logs(session, pagination, **filters)
    else:
        logs, pagination = get_user_logs(
            session, current_user.id, pagination, **filters
        )

    table_headers = [
        "Task Name",
        "User",
        "Hours Worked",
        "Description",
        "Date",
        "Task Status",
        "Actions",
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
            "allowed_filter_fields": [
                "Task Name",
                "User",
                "Hours Worked",
                "Description",
                "Task Status",
            ],
        },
    )
