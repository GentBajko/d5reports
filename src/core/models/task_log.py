from datetime import datetime

from ulid import ULID

from src.core.enums.task_status import TaskStatus


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
        self.timestamp = timestamp
        self.task_id = task_id
        self.task_name = task_name
        self.description = description
        self.user_id = user_id
        self.time_spent_today = hours_spent_today
        self.task_status = task_status

    @property
    def _timestamp(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp)

    @property
    def _task_id(self) -> ULID:
        return ULID.from_str(self.task_id)

    @property
    def _task_status(self) -> TaskStatus:
        return TaskStatus(self.task_status)
