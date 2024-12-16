from typing import Union
from fastapi import Depends, Request, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from backend.dependencies import get_session
from backend.dependencies.auth import get_current_user
from core.models.user import User
from database.interfaces.session import ISession

dashboard_router = APIRouter()


@dashboard_router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    session: ISession = Depends(get_session),
    current_user: Union[User, RedirectResponse] = Depends(get_current_user),
):
    if isinstance(current_user, User):
        return RedirectResponse(url="/task")
    request.session.clear()
    return RedirectResponse(url="/user/login")
