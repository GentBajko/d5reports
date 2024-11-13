from fastapi import Form, Depends, Request, APIRouter, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.backend.models import (
    UserCreateModel,
    UserResponseModel,
)
from src.database.models import user_mapper  # noqa F401
from src.core.models.user import User
from src.backend.dependencies import get_session
from src.backend.views.user_view import (
    get_user,
    create_user,
    update_user,
    upsert_user,
    get_all_users,
    authenticate_user,
)
from src.backend.dependencies.auth import validate_csrf, get_current_user
from src.database.interfaces.session import ISession

templates = Jinja2Templates(directory="src/backend/templates")

user_router = APIRouter(prefix="/user")


@user_router.post("/")
async def create_user_endpoint(
    request: Request,
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    permissions: int = Form(...),
    session: ISession = Depends(get_session),
    csrf_protect=Depends(validate_csrf),
):
    user = UserCreateModel(
        email=email,
        full_name=full_name,
        password=password,
        permissions=permissions,
    )
    return create_user(user, session)


@user_router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("user_login.html", {"request": request})


@user_router.post("/login")
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session: ISession = Depends(get_session),
    csrf_protect=Depends(validate_csrf),
):
    authenticated_user = authenticate_user(email, password, session)
    if not authenticated_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    request.session["user_id"] = authenticated_user.id
    return RedirectResponse(url="/", status_code=302)


@user_router.post("/logout")
async def logout(
    request: Request,
    csrf_protect=Depends(validate_csrf),
):
    request.session.clear()
    return RedirectResponse(url="/user_login", status_code=302)


@user_router.get("/{user_id}", response_class=HTMLResponse)
def get_user_endpoint(
    request: Request, user_id: str, session: ISession = Depends(get_session)
):
    user = get_user(session, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    template_name = (
        "user_detail_htmx.html"
        if request.headers.get("HX-Request")
        else "user_detail.html"
    )
    return templates.TemplateResponse(
        template_name, {"request": request, "user": user}
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
    request: Request,
    session: ISession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    users = get_all_users(session)
    return templates.TemplateResponse(
        "users.html", {"request": request, "users": users}
    )