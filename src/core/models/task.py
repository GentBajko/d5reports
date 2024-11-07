from typing import TYPE_CHECKING, List

from ulid import ULID

from core.enums.task_status import TaskStatus
if TYPE_CHECKING:
    from core.models.task_log import TaskLog


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
        self._id = id
        self._project_id = project_id
        self.project_name = project_name
        self.user_id = user_id
        self.title = title
        self.hours_required = hours_required
        self.description = description
        self._logs = logs
        self._status = status

    @property
    def id(self) -> str:
        return ULID.from_str(self._id)

    @property
    def project_id(self) -> str:
        return ULID.from_str(self._project_id)

    @property
    def status(self) -> str:
        return TaskStatus(self._status)

    @property
    def logs(self) -> List[str]:
        return [ULID.from_str(log) for log in self._logs]

    @property
    def status_str(self) -> str:
        return ULID.from_str(self._status)
