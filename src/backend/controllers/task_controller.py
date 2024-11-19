from ulid import ULID
from fastapi import Form, Depends, Request, APIRouter, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.models import TaskCreateModel, TaskResponseModel
from database.models import task_mapper  # noqa F401
from core.models.user import User
from backend.dependencies import get_session
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
    validate_csrf,
    get_current_user,
)
from database.interfaces.session import ISession

templates = Jinja2Templates(directory="src/backend/templates")

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
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint to retrieve all tasks.
    """
    tasks = get_all_tasks(session)
    headers = ["Title", "Project", "User", "Status"]
    data = [
        {
            "id": task.id,
            "title": task.title,
            "project_id": task.project_id,
            "project_name": task.project_name,
            "user_id": task.user_id,
            "user_name": task.user_name,
            "status": task.status,
        }
        for task in tasks
    ]
    return templates.TemplateResponse(
        "task/tasks.html",
        {"request": request, "headers": headers, "data": data},
    )


@task_router.get("/project/{project_id}", response_class=HTMLResponse)
def get_tasks_by_project_endpoint(
    request: Request,
    project_id: str,
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint to retrieve tasks by project.
    """
    tasks = get_project_tasks(session, project_id)
    headers = ["Title", "User", "Status"]
    data = [
        {
            "id": task.id,
            "title": task.title,
            "user_name": task.user_id,
            "status": task.status,
        }
        for task in tasks
    ]
    return templates.TemplateResponse(
        "task/tasks.html",
        {"request": request, "headers": headers, "data": data},
    )


@task_router.get("/", response_class=HTMLResponse)
def get_tasks_by_user_endpoint(
    request: Request,
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint to retrieve tasks by user.
    """
    tasks = get_user_tasks(session, current_user.id)
    headers = ["Title", "Project", "Status"]
    data = [
        {
            "id": task.id,
            "title": task.title,
            "project_name": task.project_name,
            "status": task.status,
        }
        for task in tasks
    ]
    return templates.TemplateResponse(
        "tasks.html", {"request": request, "headers": headers, "data": data}
    )
