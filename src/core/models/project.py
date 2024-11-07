from typing import TYPE_CHECKING, List

from ulid import ULID

if TYPE_CHECKING:
    from core.models.task import Task
    from core.models.user import User


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
        self._id = id
        self.name = name
        self.email = email
        self.developers = developers
        self.tasks = tasks
        self.send_email = send_email

    @property
    def id(self) -> str:
        return ULID.from_str(self._id)
