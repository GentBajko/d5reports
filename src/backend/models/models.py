from typing import List, Optional, Union

from pydantic import Field, EmailStr, BaseModel


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
    developers: Union[List["UserResponseModel"], str] = Field(default_factory=list)
    tasks: Union[List[TaskResponseModel], str] = Field(default_factory=list)


class UserCreateModel(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    permissions: int


class UserResponseModel(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    permissions: int
    tasks: Optional[List[TaskResponseModel]] = Field(default=None)
    projects: Optional[List[ProjectResponseModel]] = Field(default=None)


class UserLoginModel(BaseModel):
    email: str
    password: str
