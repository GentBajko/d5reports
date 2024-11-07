from typing import TYPE_CHECKING, List

from ulid import ULID

from src.core.enums.premissions import Permissions

if TYPE_CHECKING:
    from src.core.models.task import Task
    from src.core.models.project import Project


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
        self.id = id
        self.email = email
        self.password = password
        self.full_name = full_name
        self.projects = projects
        self.tasks = tasks
        self.permissions = permissions

    @property
    def _id(self) -> ULID:
        return ULID.from_str(self.id)

    @property
    def _permissions(self) -> Permissions:
        return Permissions(self.permissions)
