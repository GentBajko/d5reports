from typing import Union
from fastapi import Depends, Request, HTTPException
from fastapi.responses import RedirectResponse

from core.models.user import User
from core.enums.premissions import Permissions
from database.interfaces.session import ISession
from backend.dependencies.db_session import get_session
from database.repositories.repository import Repository


def get_current_user(
    request: Request, session: ISession = Depends(get_session)
) -> Union[User, RedirectResponse]:
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/user/login")
    with session as s:
        repository = Repository(s, User)
        user = repository.get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
    return user


def is_admin(current_user: User) -> bool:
    return Permissions(current_user.permissions) == Permissions.ADMIN


async def validate_csrf(request: Request):
    csrf_token_in_session = request.session.get("csrftoken", "")
    csrf_token = request.headers.get("X-CSRFToken", "")
    if not csrf_token:
        form = await request.form()
        csrf_token = form.get("csrftoken", "")
    if not csrf_token or csrf_token != csrf_token_in_session:
        raise HTTPException(status_code=400, detail="Invalid CSRF token")
