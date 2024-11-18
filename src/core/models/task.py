from typing import TYPE_CHECKING, List, Optional

from ulid import ULID

from src.core.enums.task_status import TaskStatus

if TYPE_CHECKING:
    from src.core.models.task_log import TaskLog


class Task:
    def __init__(
        self,
        project_id: str,
        user_id: str,
        title: str,
        hours_required: float,
        description: str,
        status: str,
        id: Optional[str] = None,
        logs: Optional[List["TaskLog"]] = None,
    ):
        self.id = id or str(ULID())
        self.project_id = project_id
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

    def to_dict(self, visited=None):
        if visited is None:
            visited = set()

        if id(self) in visited:
            return {"id": self.id}

        visited.add(id(self))

        return {
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "title": self.title,
            "hours_required": self.hours_required,
            "description": self.description,
            "status": self.status,
            "logs": [log.to_dict(visited) for log in self.logs]
            if self.logs
            else [],
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            project_id=data["project_id"],
            user_id=data["user_id"],
            title=data["title"],
            hours_required=data["hours_required"],
            description=data["description"],
            status=data["status"],
            logs=[TaskLog.from_dict(log) for log in data.get("logs", [])],
        )
