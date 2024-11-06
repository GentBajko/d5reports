from datetime import datetime

from ulid import ULID

from core.enums.task_status import TaskStatus


class TaskLog:
    def __init__(
        self,
        timestamp: int,
        task_id: str,
        task_name: str,
        description: str,
        user_id: str,
        hours_spent_today: int,
        task_status: str,
    ):
        self._timestamp = timestamp
        self._task_id = task_id
        self.task_name = task_name
        self.description = description
        self.user_id = user_id
        self.time_spent_today = hours_spent_today
        self._task_status = task_status

    @property
    def timestamp(self) -> datetime:
        return datetime.fromtimestamp(self._timestamp)

    @property
    def task_status(self) -> TaskStatus:
        return TaskStatus(self._task_status)

    @property
    def task_id(self) -> ULID:
        return ULID.from_str(self._task_id)
