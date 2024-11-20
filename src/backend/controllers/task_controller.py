from typing import Optional

from ulid import ULID
from fastapi import Form, Depends, Request, APIRouter, HTTPException
from sqlalchemy import asc, desc
from fastapi.responses import HTMLResponse, RedirectResponse

from backend.models import TaskCreateModel, TaskResponseModel
from database.models import task_mapper  # noqa F401
from core.models.task import Task
from core.models.user import User
from backend.dependencies import get_session
from backend.utils.templates import templates
from backend.views.task_view import (
    get_task,
    create_task,
    update_task,
    upsert_task,
    get_all_tasks,
    get_user_tasks,
    get_project_tasks,
)
from backend.dependencies.auth import (
    is_admin,
    validate_csrf,
    get_current_user,
)
from backend.models.pagination import Pagination
from database.interfaces.session import ISession

task_router = APIRouter(prefix="/task")


@task_router.get("/create")
def get_task_home(
    request: Request, current_user: User = Depends(get_current_user)
):
    """
    Endpoint to retrieve the task home page.
    """
    return templates.TemplateResponse("task/create.html", {"request": request})


@task_router.post("/", response_class=HTMLResponse)
async def create_task_endpoint(
    request: Request,
    project_name: str = Form(...),
    title: str = Form(...),
    hours_required: float = Form(...),
    description: str = Form(...),
    status: str = Form(...),
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    csrf_protect=Depends(validate_csrf),
):
    """
    Endpoint to create a new task.
    """

    task_data = TaskCreateModel(
        project_id=str(ULID()),
        project_name=project_name,
        user_id=current_user.id,
        user_name=current_user.full_name,
        title=title,
        hours_required=hours_required,
        description=description,
        status=status,
    )
    try:
        task = create_task(task_data, session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return RedirectResponse(f"/task/{task.id}", status_code=303)


@task_router.get("/{task_id}", response_class=HTMLResponse)
def get_task_endpoint(
    request: Request,
    task_id: str,
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint to retrieve a specific task.
    """
    try:
        task = get_task(session, id=task_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return templates.TemplateResponse(
        "task/detail.html", {"request": request, "task": task}
    )


@task_router.put("/{task_id}", response_model=TaskResponseModel)
def update_task_endpoint(
    task_id: str,
    task_update: TaskCreateModel,
    session: ISession = Depends(get_session),
):
    """
    Endpoint to update an existing task.
    """
    try:
        task = update_task(task_id, task_update, session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return task


@task_router.post("/upsert", response_model=TaskResponseModel)
def upsert_task_endpoint(
    task: TaskResponseModel, session: ISession = Depends(get_session)
):
    """
    Endpoint to upsert a task.
    """
    try:
        task = upsert_task(task, session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return task


@task_router.get("/", response_class=HTMLResponse)
def get_all_tasks_endpoint(
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
        "Title": "title",
        "Hours Required": "hours_required",
        "Status": "status",
        "Timestamp": "timestamp",
    }

    if sort:
        sort_field = sort_mapping.get(sort)
        if sort_field:
            sort_column = getattr(Task, sort_field, None)
            if sort_column:
                if order and order.lower() == "desc":
                    order_by.append(desc(sort_column))
                else:
                    order_by.append(asc(sort_column))

    pagination = Pagination(limit=limit, current_page=page, order_by=order_by)

    if is_admin(current_user):
        tasks, pagination = get_all_tasks(session, pagination)
    else:
        tasks, pagination = get_user_tasks(
            session, current_user.id, pagination
        )

    print([task.timestamp for task in tasks])

    table_headers = [
        "Title",
        "Hours Required",
        "Description",
        "Timestamp",
        "Status",
        "Logs",
    ]

    return templates.TemplateResponse(
        "task/tasks.html",
        {
            "request": request,
            "headers": table_headers,
            "data": tasks,
            "pagination": pagination,
            "entity": "task",
            "current_sort": sort,
            "current_order": order,
        },
    )


@task_router.get("/project/{project_id}", response_class=HTMLResponse)
def get_tasks_by_project_endpoint(
    request: Request,
    project_id: str,
    page: int = 1,
    sort: Optional[str] = None,
    order: Optional[str] = None,
    limit: int = 15,
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    order_by = []
    if sort:
        sort_column = getattr(Task, sort, None)
        if sort_column:
            if order and order.lower() == "desc":
                order_by.append(desc(sort_column))
            else:
                order_by.append(asc(sort_column))
        else:
            raise HTTPException(
                status_code=400, detail=f"Invalid sort field: {sort}"
            )

    pagination = Pagination(limit=limit, current_page=page, order_by=order_by)

    tasks, pagination = get_project_tasks(session, project_id, pagination)

    context = {
        "request": request,
        "headers": [
            "Title",
            "Hours Required",
            "Description",
            "Status",
            "Logs",
        ],
        "data": tasks,
        "pagination": pagination,
        "entity": "task",
        "current_sort": sort,
        "current_order": order,
    }
    return templates.TemplateResponse("task/tasks.html", context)


@task_router.get("/user/{user_id}", response_class=HTMLResponse)
def get_tasks_by_user_endpoint(
    request: Request,
    user_id: str,
    page: int = 1,
    sort: Optional[str] = None,
    order: Optional[str] = None,
    limit: int = 15,
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    order_by = []
    if sort:
        sort_column = getattr(Task, sort, None)
        if sort_column:
            if order and order.lower() == "desc":
                order_by.append(desc(sort_column))
            else:
                order_by.append(asc(sort_column))
        else:
            raise HTTPException(
                status_code=400, detail=f"Invalid sort field: {sort}"
            )

    pagination = Pagination(limit=limit, current_page=page, order_by=order_by)

    if current_user.id != user_id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Access forbidden")

    tasks, pagination = get_user_tasks(session, user_id, pagination)

    context = {
        "request": request,
        "headers": [
            "Title",
            "Hours Required",
            "Description",
            "Status",
            "Logs",
        ],
        "data": tasks,
        "pagination": pagination,
        "entity": "task",
        "current_sort": sort,
        "current_order": order,
    }
    return templates.TemplateResponse("task/tasks.html", context)
