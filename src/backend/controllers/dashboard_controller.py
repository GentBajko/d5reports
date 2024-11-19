# In user_controller.py
from fastapi import Depends, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backend.dependencies import get_session
from core.enums.premissions import Permissions
from backend.views.user_view import get_all_users
from database.interfaces.session import ISession

templates = Jinja2Templates(directory="src/backend/templates")
dashboard_router = APIRouter()


@dashboard_router.get("/", response_class=HTMLResponse)
async def home(request: Request, session: ISession = Depends(get_session)):
    users = get_all_users(session)
    headers = ["Email", "Full Name", "Permissions"]
    data = [
        {
            "full name": user.full_name,
            "email": user.email,
            "permissions": str(Permissions(user.permissions)),
        }
        for user in users
    ]
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "headers": headers,
            "data": data,
        },
    )
