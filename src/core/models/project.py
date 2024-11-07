from typing import TYPE_CHECKING, List

from ulid import ULID

if TYPE_CHECKING:
    from src.core.models.task import Task
    from src.core.models.user import User


class Project:
    def __init__(
        self,
        id: str,
        name: str,
        email: str,
        developers: List["User"],
        tasks: List["Task"],
        send_email: bool,
    ):
        self.id = ULID.from_str(id)
        self.name = name
        self.email = email
        self.developers = developers
        self.tasks = tasks
        self.send_email = send_email

    @property
    def _id(self) -> str:
        return str(self.id)
