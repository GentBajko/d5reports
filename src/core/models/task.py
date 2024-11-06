from ulid import ULID

from core.enums.task_status import TaskStatus


class Task:
    def __init__(
        self,
        id: str,
        project_id: str,
        project_name: str,
        title: str,
        hours_required: int,
        description: str,
        status: str,
    ):
        self._id = id
        self._project_id = project_id
        self.project_name = project_name
        self.title = title
        self.hours_required = hours_required
        self.description = description
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
