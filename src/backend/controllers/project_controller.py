from typing import List

from fastapi import Form, Depends, Request, APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.backend.models import (
    ProjectCreateModel,
    ProjectResponseModel,
)
from src.database.models import project_mapper  # noqa F401
from src.core.models.user import User
from src.backend.dependencies import get_session
from src.backend.dependencies.auth import (
    is_admin,
    validate_csrf,
    get_current_user,
)
from src.backend.views.project_view import (
    get_project,
    create_project,
    update_project,
    upsert_project,
    get_all_projects,
    get_users_projects,
    assign_project_to_user,
)
from src.database.interfaces.session import ISession

templates = Jinja2Templates(directory="src/backend/templates")

project_router = APIRouter(prefix="/project")


@project_router.post("/")
async def create_project_endpoint(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    send_email: bool = Form(...),
    archived: bool = Form(...),
    session: ISession = Depends(get_session),
    csrf_protect=Depends(validate_csrf),
):
    project = ProjectCreateModel(
        name=name,
        email=email,
        send_email=send_email,
        archived=archived,
    )
    return create_project(project, session)


@project_router.get("/{project_id}", response_class=HTMLResponse)
def get_project_endpoint(
    request: Request, project_id: str, session: ISession = Depends(get_session)
):
    project = get_project(session, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return templates.TemplateResponse(
        "project/detail.html", {"request": request, "project": project}
    )


@project_router.put("/{project_id}", response_model=ProjectResponseModel)
def update_project_endpoint(
    project_id: str,
    project_update: ProjectCreateModel,
    session: ISession = Depends(get_session),
):
    return update_project(project_id, project_update, session)


@project_router.post("/upsert", response_model=ProjectResponseModel)
def upsert_project_endpoint(
    project: ProjectCreateModel, session: ISession = Depends(get_session)
):
    return upsert_project(project, session)


@project_router.get("/", response_class=HTMLResponse)
def get_all_projects_endpoint(
    request: Request,
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    projects = (
        get_all_projects(session)
        if is_admin(current_user)
        else [project for project in get_users_projects(current_user.id, session)]
    )
    print(projects)
    table_headers = ["Name", "Email", "Send Email", "Archived", "Developers", "Tasks"]
    return templates.TemplateResponse(
        "project/projects.html", {"request": request, "headers": table_headers, "data": projects}
    )


@project_router.get(
    "/{user_id}/user_projects", response_model=List[ProjectResponseModel]
)
def get_users_projects_endpoint(
    request: Request,
    user_id: str,
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=403, detail="Access forbidden")


@project_router.post(
    "/{project_id}/assign_user", response_model=ProjectResponseModel
)
def assign_project_to_user_endpoint(
    project_id: str,
    user_id: str = Form(...),
    session: ISession = Depends(get_session),
):
    return assign_project_to_user(project_id, user_id, session)
