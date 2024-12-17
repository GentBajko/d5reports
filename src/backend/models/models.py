from typing import List, Optional
from datetime import datetime

from ulid import ULID
from pydantic import Field, EmailStr, BaseModel, validator


class LogCreateModel(BaseModel):
    task_name: str
    description: str
    hours_spent_today: float
    task_status: str
    id: str = Field(default=str(ULID()))
    user_id: str
    user_name: str
    timestamp: int = Field(default=datetime.now().timestamp())
    task_id: str = Field(default=str(ULID()))


class LogResponseModel(BaseModel):
    id: str
    task_name: str
    description: str
    user_id: str
    user_name: str
    hours_spent_today: float
    task_status: str
    timestamp: int = Field(default=datetime.now().timestamp())
    task_id: str = Field(default=str(ULID()))


class TaskCreateModel(BaseModel):
    project_id: str
    project_name: str
    user_id: str
    user_name: str
    title: str
    hours_required: float
    hours_worked: float = 0.0
    returned: bool = False
    description: str
    status: Optional[str] = None
    timestamp: int = Field(default=int(datetime.now().timestamp()))


class TaskResponseModel(BaseModel):
    id: str
    project_id: str
    project_name: str
    user_id: str
    user_name: str
    title: str
    hours_required: float
    hours_worked: float
    returned: bool = False
    description: str
    logs: List[LogCreateModel]
    status: Optional[str] = None
    last_updated: Optional[int] = Field(default=None)
    timestamp: int = Field(default=int(datetime.now().timestamp()))


class ProjectCreateModel(BaseModel):
    name: str
    send_email: bool
    email: Optional[EmailStr] = None
    archived: bool = False

    @validator('email', pre=True, always=True)
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v

class ProjectResponseModel(BaseModel):
    id: str
    name: str
    send_email: bool
    archived: bool
    email: Optional[EmailStr] = None
    developers: List["UserResponseModel"] = Field(default_factory=list)
    tasks: List[TaskResponseModel] = Field(default_factory=list)

    @validator('email', pre=True, always=True)
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v

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
    tasks: List[TaskResponseModel] = Field(default_factory=list)
    projects: List["ProjectResponseModel"] = Field(default_factory=list)


class UserLoginModel(BaseModel):
    email: str
    password: str


UserResponseModel.model_rebuild()
ProjectResponseModel.model_rebuild()
TaskResponseModel.model_rebuild()
LogResponseModel.model_rebuild()
