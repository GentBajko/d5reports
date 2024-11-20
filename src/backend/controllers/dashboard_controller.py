from fastapi import Depends, Request, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.dependencies import get_session
from backend.dependencies.auth import get_current_user
from database.interfaces.session import ISession

templates = Jinja2Templates(directory="src/backend/templates")
dashboard_router = APIRouter()


@dashboard_router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    session: ISession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    if current_user:
        return RedirectResponse(url="/task")
    return RedirectResponse(url="/user/login")
