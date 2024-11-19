from typing import TYPE_CHECKING, List, Optional

from ulid import ULID

from core.enums.premissions import Permissions

if TYPE_CHECKING:
    from core.models.task import Task
    from core.models.project import Project


class User:
    def __init__(
        self,
        email: str,
        password: str,
        full_name: str,
        permissions: int,
        id: Optional[str] = None,
        projects: Optional[List["Project"]] = None,
        tasks: Optional[List["Task"]] = None,
    ):
        self.id = id or str(ULID())
        self.email = email
        self.password = password
        self.full_name = full_name
        self.projects = projects
        self.tasks = tasks
        self.permissions = permissions

    @property
    def _id(self) -> ULID:
        return ULID.from_str(self.id)

    @property
    def _permissions(self) -> Permissions:
        return Permissions(self.permissions)

    def to_dict(self, visited=None):
        if visited is None:
            visited = set()

        if id(self) in visited:
            return {"id": self.id}

        visited.add(id(self))

        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "permissions": self.permissions,
            "projects": [project.to_dict(visited) for project in self.projects]
            if self.projects
            else [],
            "tasks": [task.to_dict(visited) for task in self.tasks]
            if self.tasks
            else [],
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            email=data["email"],
            password=data["password"],
            full_name=data["full_name"],
            permissions=data["permissions"],
            projects=[
                Project.from_dict(project)
                for project in data.get("projects", [])
            ],
            tasks=[Task.from_dict(task) for task in data.get("tasks", [])],
        )
