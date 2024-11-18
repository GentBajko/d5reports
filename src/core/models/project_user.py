from typing import Dict


class ProjectUser:
    def __init__(self, project_id: str, user_id: str):
        self.project_id = project_id
        self.user_id = user_id

    def to_dict(self) -> Dict[str, str]:
        return {"project_id": self.project_id, "user_id": self.user_id}

    def from_dict(self, data: Dict[str, str]) -> None:
        self.project_id = data["project_id"]
        self.user_id = data["user_id"]
