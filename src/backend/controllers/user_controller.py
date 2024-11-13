from fastapi import Depends, APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from src.backend.models import (
    UserCreateModel,
    UserResponseModel,
)
from src.database.models import user_mapper  # noqa F401
from src.backend.dependencies import get_session
from src.backend.views.user_view import (
    get_user,
    create_user,
    update_user,
    upsert_user,
    get_all_users,
)
from src.database.interfaces.session import ISession
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="src/backend/templates")

user_router = APIRouter(prefix="/user")


@user_router.post("/", response_model=UserResponseModel)
def create_user_endpoint(
    user: UserCreateModel, session: ISession = Depends(get_session)
):
    return create_user(user, session)

@user_router.get("/test", response_class=HTMLResponse)
def test_template(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@user_router.get("/{user_id}", response_class=HTMLResponse)
def get_user_endpoint(
    request: Request, user_id: str, session: ISession = Depends(get_session)
):
    user = get_user(session, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse(
        "user_detail.html", {"request": request, "user": user}
    )


@user_router.put("/{user_id}", response_model=UserResponseModel)
def update_user_endpoint(
    user_id: str,
    user_update: UserCreateModel,
    session: ISession = Depends(get_session),
):
    return update_user(user_id, user_update, session)


@user_router.post("/upsert", response_model=UserResponseModel)
def upsert_user_endpoint(
    user: UserCreateModel, session: ISession = Depends(get_session)
):
    return upsert_user(user, session)


@user_router.get("/", response_class=HTMLResponse)
def get_all_users_endpoint(
    request: Request, session: ISession = Depends(get_session)
):
    users = get_all_users(session)
    return templates.TemplateResponse(
        "users.html", {"request": request, "users": users}
    )
