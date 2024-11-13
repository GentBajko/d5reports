from fastapi import Depends, Request, HTTPException

from src.core.models.user import User
from src.core.enums.premissions import Permissions
from src.database.adapters.mysql import MySQL
from src.database.interfaces.session import ISession
from src.backend.dependencies.db_session import get_session
from src.database.repositories.repository import Repository


def get_current_user(
    request: Request, session: ISession = Depends(get_session)
) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    with session as s:
        repository = Repository(s, User)
        user = repository.get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
    return user


def is_admin(**kwargs) -> bool:
    with MySQL.session() as s:
        repository = Repository(s, User)  # type: ignore
        user = repository.query(**kwargs)[0]
        return Permissions(user.permissions) == Permissions.ADMIN


async def validate_csrf(request: Request):
    csrf_token_in_session = request.session.get("csrftoken", "")
    csrf_token = request.headers.get("X-CSRFToken", "")
    if not csrf_token:
        form = await request.form()
        csrf_token = form.get("csrftoken", "")
    if not csrf_token or csrf_token != csrf_token_in_session:
        raise HTTPException(status_code=400, detail="Invalid CSRF token")
