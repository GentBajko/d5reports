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
        self.timestamp = datetime.fromtimestamp(timestamp)
        self.task_id = ULID.from_str(task_id)
        self.task_name = task_name
        self.description = description
        self.user_id = user_id
        self.time_spent_today = hours_spent_today
        self.task_status = TaskStatus(task_status)

    @property
    def _timestamp(self) -> float:
        return self.timestamp.timestamp()

    @property
    def _task_id(self) -> str:
        return str(self.task_id)

    @property
    def _task_status(self) -> str:
        return self.task_status.value
