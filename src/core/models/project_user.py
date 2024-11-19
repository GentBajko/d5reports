from typing import Dict

from ulid import ULID


class ProjectUser:
    def __init__(self, id: str, project_id: str, user_id: str):
        self.id = id
        self.project_id = project_id
        self.user_id = user_id

    @property
    def _id(self) -> ULID:
        return ULID.from_str(self.id)

    def to_dict(self) -> Dict[str, str]:
        return {"project_id": self.project_id, "user_id": self.user_id}

    def from_dict(self, data: Dict[str, str]) -> None:
        self.project_id = data["project_id"]
        self.user_id = data["user_id"]
