from random import choice
from datetime import datetime

from ulid import ULID
from argon2 import PasswordHasher

from core.models.log import Log
from database.models import (  # noqa F401
    log_mapper,
    task_mapper,
    user_mapper,
    project_mapper,
    project_developers_table,
)
from core.models.task import Task
from core.models.user import User
from core.models.project import Project
from core.enums.premissions import Permissions
from core.enums.task_status import TaskStatus
from database.adapters.mysql import MySQL
from core.models.project_user import ProjectUser
from database.repositories.repository import Repository
from database.sessions.sqlalchemy_session import SQLAlchemySession

ph = PasswordHasher()
hashed_password = ph.hash("password")

users = [
    User(
        id=str(ULID()),
        full_name=f"John Doe{i}",
        email=f"john.doe{i}@mail.com",
        password=hashed_password,
        permissions=Permissions.DEVELOPER.value,
        projects=[],
        tasks=[],
    )
    for i in range(100)
]
users.append(
    User(
        id=str(ULID()),
        full_name="Jane Doe",
        email="jane.doe@mail.com",
        password=hashed_password,
        permissions=Permissions.ADMIN.value,
        projects=[],
        tasks=[],
    )
)

projects = [
    Project(
        id=str(ULID()),
        name=f"Project {i}",
        email=f"project{i}@mail.com",
        send_email=(i % 2 == 0),
        archived=(i % 2 != 0),
        developers=[],
        tasks=[],
    )
    for i in range(10)
]

seen_pairs = set()
project_users = []
while len(project_users) < 100:
    project_id = choice(projects).id
    user_id = choice(users).id
    pair = (project_id, user_id)

    if pair not in seen_pairs:
        seen_pairs.add(pair)
        project_users.append(
            ProjectUser(
                id=str(ULID()),
                project_id=project_id,
                user_id=user_id,
            )
        )

tasks = []
for i in range(100):
    project = choice(projects)
    user = choice(users)
    task = Task(
        id=str(ULID()),
        project_id=project.id,
        project_name=project.name,
        user_id=user.id,
        user_name=user.full_name,
        title=f"Task {i}",
        hours_required=i + 1,
        description=f"Task {i} description",
        status=choice([status.value for status in TaskStatus]),
        timestamp=int(datetime.now().timestamp()) + (i * 1000),
        logs=[],
    )
    tasks.append(task)

logs = []
for i in range(100):
    task = choice(tasks)
    log = Log(
        id=str(ULID()),
        task_id=task.id,
        user_id=choice(users).id,
        description=f"Task {i} log description",
        timestamp=int(datetime.now().timestamp()),
        hours_spent_today=i + 1,
        task_status=task.status,
        task_name=task.title,
    )
    logs.append(log)

with SQLAlchemySession(MySQL.session()) as s:
    user_repo = Repository(s, User)
    project_repo = Repository(s, Project)
    task_repo = Repository(s, Task)
    log_repo = Repository(s, Log)

    project_user_table = Repository(s, ProjectUser)

    for user in users:
        user_repo.create(user)
    for project in projects:
        project_repo.create(project)
    for task in tasks:
        task_repo.create(task)
    for log in logs:
        log_repo.create(log)
    for project_user in project_users:
        project_user_table.create(project_user)
