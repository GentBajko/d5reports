from typing import TYPE_CHECKING, List

from ulid import ULID

from src.core.enums.task_status import TaskStatus

if TYPE_CHECKING:
    from src.core.models.task_log import TaskLog


class Task:
    def __init__(
        self,
        id: str,
        project_id: str,
        project_name: str,
        user_id: str,
        title: str,
        hours_required: float,
        description: str,
        logs: List["TaskLog"],
        status: str,
    ):
        self.id = ULID.from_str(id)
        self.project_id = project_id
        self.project_name = project_name
        self.user_id = user_id
        self.title = title
        self.hours_required = hours_required
        self.description = description
        self.logs = logs
        self.status = status

    @property
    def _id(self) -> ULID:
        return ULID.from_str(self.id)

    @property
    def _project_id(self) -> ULID:
        return ULID.from_str(self.project_id)

    @property
    def _status(self) -> TaskStatus:
        return TaskStatus(self.status)
