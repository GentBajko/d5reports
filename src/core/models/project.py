from typing import TYPE_CHECKING, List, Optional

from ulid import ULID

if TYPE_CHECKING:
    from core.models.task import Task
    from core.models.user import User


class Project:
    if TYPE_CHECKING:
        id: str
        name: str
        email: Optional[str]
        developers: Optional[List["User"]]
        tasks: Optional[List["Task"]]
        send_email: bool
        archived: bool
    
    def __init__(
        self,
        name: str,
        send_email: bool,
        archived: bool,
        email: Optional[str] = None,
        id: Optional[str] = None,
        developers: Optional[List["User"]] = None,
        tasks: Optional[List["Task"]] = None,
    ):
        self.id = id or str(ULID())
        self.name = name
        self.email = email
        self.developers = developers
        self.tasks = tasks
        self.send_email = send_email
        self.archived = archived

    @property
    def _id(self) -> ULID:
        return ULID.from_str(id)

    def to_dict(self, visited=None):
        if visited is None:
            visited = set()

        if id(self) in visited:
            return {
                "id": self.id,
                "name": self.name,
                "email": self.email,
                "send_email": self.send_email,
                "archived": self.archived,
            }

        visited.add(id(self))

        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "send_email": self.send_email,
            "archived": self.archived,
            "developers": [
                developer.to_dict(visited) for developer in self.developers
            ]
            if self.developers
            else [],
            "tasks": [task.to_dict(visited) for task in self.tasks]
            if self.tasks
            else [],
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            send_email=data["send_email"],
            archived=data["archived"],
            developers=[
                User.from_dict(developer)
                for developer in data.get("developers", [])
            ],
            tasks=[Task.from_dict(task) for task in data.get("tasks", [])],
        )
