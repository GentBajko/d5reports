from datetime import datetime

from ulid import ULID

from core.enums.task_status import TaskStatus


class TaskLog:
    def __init__(
        self,
        id: str,
        timestamp: int,
        task_id: str,
        task_name: str,
        description: str,
        user_id: str,
        hours_spent_today: int,
        task_status: str,
    ):
        self.id = id
        self.timestamp = timestamp
        self.task_id = task_id
        self.task_name = task_name
        self.description = description
        self.user_id = user_id
        self.hours_spent_today = hours_spent_today
        self.task_status = task_status

    @property
    def _id(self) -> ULID:
        return ULID.from_str(self.id)

    @property
    def _timestamp(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp)

    @property
    def _task_id(self) -> ULID:
        return ULID.from_str(self.task_id)

    @property
    def _task_status(self) -> TaskStatus:
        return TaskStatus(self.task_status)

    def to_dict(self, visited=None):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "task_id": self.task_id,
            "task_name": self.task_name,
            "description": self.description,
            "user_id": self.user_id,
            "hours_spent_today": self.hours_spent_today,
            "task_status": self.task_status,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            timestamp=data["timestamp"],
            task_id=data["task_id"],
            task_name=data["task_name"],
            description=data["description"],
            user_id=data["user_id"],
            hours_spent_today=data["hours_spent_today"],
            task_status=data["task_status"],
        )
