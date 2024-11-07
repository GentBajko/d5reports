from typing import TYPE_CHECKING, List

from ulid import ULID

from core.enums.premissions import Permissions

if TYPE_CHECKING:
    from core.models.task import Task
    from core.models.project import Project


class User:
    def __init__(
        self,
        id: str,
        email: str,
        password: str,
        full_name: str,
        projects: List["Project"],
        tasks: List["Task"],
        permissions: int,
    ):
        self._id = id
        self.email = email
        self.password = password
        self.full_name = full_name
        self.projects = projects
        self.tasks = tasks
        self._permissions = permissions

    @property
    def id(self) -> ULID:
        return ULID.from_str(self._id)

    @property
    def permissions(self) -> Permissions:
        return Permissions(self._permissions)
