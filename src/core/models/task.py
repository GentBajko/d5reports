from typing import TYPE_CHECKING, List, Optional
from datetime import datetime

from ulid import ULID

from core.enums.task_status import TaskStatus

if TYPE_CHECKING:
    from core.models.log import Log


class Task:
    if TYPE_CHECKING:
        id: str
        project_id: str
        project_name: str
        user_id: str
        user_name: str
        title: str
        hours_required: float
        returned: bool
        description: str
        status: Optional[str]
        timestamp: int
        hours_worked: float
        last_updated: Optional[int]
        logs: Optional[List["Log"]]

    def __init__(
        self,
        project_id: str,
        project_name: str,
        user_id: str,
        user_name: str,
        title: str,
        hours_required: float,
        description: str,
        timestamp: int,
        hours_worked: float = 0.0,
        returned: bool = False,
        last_updated: Optional[int] = None,
        status: Optional[str] = None,
        id: Optional[str] = None,
        logs: Optional[List["Log"]] = None,
    ):
        self.id = id or str(ULID())
        self.project_id = project_id
        self.project_name = project_name
        self.user_id = user_id
        self.user_name = user_name
        self.title = title
        self.hours_required = hours_required
        self.returned = returned
        self.description = description
        self.logs = logs
        self.status = status
        self.timestamp = timestamp
        self.hours_worked = hours_worked
        self.last_updated = last_updated

    @property
    def _id(self) -> ULID:
        return ULID.from_str(self.id)

    @property
    def _project_id(self) -> ULID:
        return ULID.from_str(self.project_id)

    @property
    def _status(self) -> Optional[TaskStatus]:
        return TaskStatus(self.status) if self.status else None

    @property
    def _timestamp(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp)

    @property
    def _last_updated(self) -> Optional[datetime]:
        return (
            datetime.fromtimestamp(self.last_updated)
            if self.last_updated
            else None
        )

    def to_dict(self, visited=None):
        if visited is None:
            visited = set()

        if id(self) in visited:
            return {
                "id": self.id,
                "project_id": self.project_id,
                "project_name": self.project_name,
                "user_id": self.user_id,
                "user_name": self.user_name,
                "title": self.title,
                "hours_required": self.hours_required,
                "last_updated": self.last_updated,
                "description": self.description,
                "status": self.status,
                "timestamp": self.timestamp,
                "hours_worked": self.hours_worked,
                "logs": [],
            }

        visited.add(id(self))

        return {
            "id": self.id,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "title": self.title,
            "hours_required": self.hours_required,
            "returned": self.returned,
            "description": self.description,
            "status": self.status,
            "timestamp": self.timestamp,
            "last_updated": self.last_updated,
            "hours_worked": self.hours_worked,
            "logs": [log.to_dict(visited) for log in self.logs]
            if self.logs
            else [],
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            project_id=data["project_id"],
            project_name=data["project_name"],
            user_id=data["user_id"],
            user_name=data["user_name"],
            title=data["title"],
            hours_required=data["hours_required"],
            returned=data.get("returned", False),
            description=data["description"],
            status=data["status"],
            timestamp=data["timestamp"],
            last_updated=data["last_updated"],
            hours_worked=data.get("hours_worked", 0.0),
            logs=[Log.from_dict(log) for log in data.get("logs", [])],
        )
