from typing import List

from ulid import ULID

from core.enums.premissions import Permissions


class User:
    def __init__(
        self,
        id: str,
        username: str,
        password: str,
        email: str,
        full_name: str,
        projects: List[str],
        tasks: List[str],
        permissions: int,
    ):
        self._id = id
        self.username = username
        self.password = password
        self.email = email
        self.full_name = full_name
        self._projects = projects
        self.tasks = tasks
        self._permissions = permissions

    @property
    def id(self) -> ULID:
        return ULID.from_str(self._id)

    @property
    def permissions(self) -> Permissions:
        return Permissions(self._permissions)

    @property
    def projects(self) -> List[str]:
        return [ULID.from_str(project) for project in self._projects]
