from typing import List, Optional

from pydantic import Field, EmailStr, BaseModel

from src.core.enums.premissions import Permissions


class TaskLogModel(BaseModel):
    timestamp: int
    task_id: str
    task_name: str
    description: str
    user_id: str
    hours_spent_today: int
    task_status: str


class TaskLogResponseModel(BaseModel):
    timestamp: int
    task_id: str
    task_name: str
    description: str
    user_id: str
    hours_spent_today: int
    task_status: str


class TaskCreateModel(BaseModel):
    project_id: str
    project_name: str
    user_id: str
    title: str
    hours_required: float
    description: str
    status: str


class TaskResponseModel(BaseModel):
    id: str
    project_id: str
    project_name: str
    user_id: str
    title: str
    hours_required: float
    description: str
    status: str
    logs: List[TaskLogModel]


class ProjectCreateModel(BaseModel):
    name: str
    email: EmailStr
    send_email: bool
    archived: bool


class ProjectResponseModel(BaseModel):
    id: str
    name: str
    email: EmailStr
    send_email: bool
    archived: bool
    developers: List["UserResponseModel"]
    tasks: List[TaskResponseModel]


class UserCreateModel(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    permissions: int = Permissions.DEVELOPER.value


class UserResponseModel(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    tasks: List[TaskResponseModel]
    permissions: int = Permissions.DEVELOPER.value
    projects: Optional[List[ProjectResponseModel]] = Field(default=None)
