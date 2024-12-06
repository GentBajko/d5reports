from typing import List, Tuple
import datetime

from backend.models import TaskCreateModel, TaskResponseModel
from core.models.log import Log
from database.models import task_mapper  # noqa F401
from core.models.task import Task
from core.models.project import Project
from backend.models.models import LogResponseModel
from backend.utils.pagination import calculate_pagination
from backend.models.pagination import Pagination
from database.interfaces.session import ISession
from database.repositories.repository import Repository


def create_task(task: TaskCreateModel, session: ISession) -> TaskResponseModel:
    """
    Create a new task in the database.
    """
    with session as s:
        project_repo = Repository(s, Project)

        project = project_repo.get(id=task.project_id)

        if not project:
            raise ValueError("Project not found")

        repo = Repository(s, Task)


        new_task = Task(
            project_id=project.id,
            project_name=project.name,
            user_id=task.user_id,
            user_name=task.user_name,
            title=task.title,
            hours_required=task.hours_required,
            description=task.description,
            timestamp=int(datetime.datetime.now().timestamp()),
            logs=[],
        )

        repo.create(new_task)
        s.commit()
        task_data = new_task.to_dict()
        task_data["project_name"] = project.name
    return TaskResponseModel.model_validate(task_data)


def get_task(session: ISession, **kwargs) -> TaskResponseModel:
    """
    Retrieve a single task from the database based on provided criteria.
    """
    with session as s:
        repo = Repository[Task](s, Task)
        project_repo = Repository(s, Project)

        task = repo.query(**kwargs, options=[Task.logs])  # type: ignore
        if not task:
            raise ValueError("Task not found")
        task_obj = task[0]
        project = project_repo.get(id=task_obj.project_id)
        task_dict = task_obj.to_dict()
        task_dict["project_name"] = project.name if project else ""
    return TaskResponseModel.model_validate(task_dict)


def update_task(
    task_id: str, task_update: TaskCreateModel, session: ISession
) -> TaskResponseModel:
    """
    Update an existing task's information.
    """
    with session as s:
        repo = Repository[Task](s, Task)
        task = repo.get(id=task_id)
        if not task:
            raise ValueError("Task not found")

        for attr, value in task_update.model_dump().items():
            setattr(task, attr, value)

        s.commit()
        task_dict = task.to_dict()
    return TaskResponseModel.model_validate(task_dict)


def upsert_task(
    task: TaskResponseModel, session: ISession
) -> TaskResponseModel:
    """
    Insert a new task or update an existing task based on unique constraints.
    """
    with session as s:
        repo = Repository[Task](s, Task)
        project_repo = Repository(s, Project)
        existing_task = repo.get(id=task.id)
        project = project_repo.query(id=task.project_id)
        if existing_task:
            for attr, value in task.model_dump().items():
                setattr(existing_task, attr, value)
            s.commit()
            task_dict = existing_task.to_dict()
        else:
            new_task = Task(
                project_id=task.project_id,
                project_name=project[0].name,
                user_id=task.user_id,
                user_name=task.user_name,
                title=task.title,
                hours_required=task.hours_required,
                description=task.description,
                status=task.status,
                timestamp=int(datetime.datetime.now().timestamp()),
                logs=[],
            )
            repo.create(new_task)
            s.commit()
            task_dict = new_task.to_dict()
    return TaskResponseModel.model_validate(task_dict)


def get_all_tasks(
    session: ISession, pagination: Pagination, **kwargs
) -> Tuple[List[TaskResponseModel], Pagination]:
    with session as s:
        repo = Repository(s, Task)
        total = repo.count(**kwargs)

        order_by = pagination.order_by

        pagination = calculate_pagination(
            total=total,
            page=pagination.current_page or 1,
            per_page=pagination.limit or 15,
        )
        pagination.order_by = order_by

        if total == 0:
            return [], pagination

        tasks = repo.query(
            order_by=pagination.order_by,
            limit=pagination.limit,
            offset=pagination.offset,
            options=[Task.logs],  # type: ignore
            **kwargs,
        )

        tasks_list = [
            TaskResponseModel.model_validate(task.to_dict()) for task in tasks
        ]

    return tasks_list, pagination


def get_project_tasks(
    session: ISession, project_id: str, pagination: Pagination, **kwargs
) -> Tuple[List[TaskResponseModel], Pagination]:
    with session as s:
        repo = Repository(s, Task)
        total = repo.count(project_id=project_id, **kwargs)

        order_by = pagination.order_by

        pagination = calculate_pagination(
            total=total,
            page=pagination.current_page or 1,
            per_page=pagination.limit or 15,
        )

        pagination.order_by = order_by

        if total == 0:
            return [], pagination

        tasks = repo.query(
            project_id=project_id,
            order_by=pagination.order_by,
            limit=pagination.limit,
            offset=pagination.offset,
            options=[Task.logs],  # type: ignore
            **kwargs,
        )

        tasks_list = [
            TaskResponseModel.model_validate(task.to_dict()) for task in tasks
        ]

    return tasks_list, pagination


def get_user_tasks(
    session: ISession, user_id: str, pagination: Pagination, **kwargs
) -> Tuple[List[TaskResponseModel], Pagination]:
    with session as s:
        repo = Repository(s, Task)
        total = repo.count(user_id=user_id, **kwargs)

        order_by = pagination.order_by

        pagination = calculate_pagination(
            total=total,
            page=pagination.current_page or 1,
            per_page=pagination.limit or 15,
        )

        pagination.order_by = order_by

        if total == 0:
            return [], pagination

        tasks = repo.query(
            user_id=user_id,
            order_by=pagination.order_by,
            limit=pagination.limit,
            offset=pagination.offset,
            options=[Task.logs],  # type: ignore
            **kwargs,
        )

        tasks_list = [
            TaskResponseModel.model_validate(task.to_dict()) for task in tasks
        ]

    return tasks_list, pagination


def get_task_logs(
    session: ISession, task_id: str, pagination: Pagination, **kwargs
) -> Tuple[List[LogResponseModel], Pagination]:
    with session as s:
        repo = Repository(s, Log)
        total = repo.count(task_id=task_id, **kwargs)

        order_by = pagination.order_by

        pagination = calculate_pagination(
            total=total,
            page=pagination.current_page or 1,
            per_page=pagination.limit or 15,
        )

        pagination.order_by = order_by

        if total == 0:
            return [], pagination

        logs = repo.query(
            task_id=task_id,
            order_by=pagination.order_by,
            limit=pagination.limit,
            offset=pagination.offset,
            **kwargs,
        )

        logs_list = [
            LogResponseModel.model_validate(log.to_dict()) for log in logs
        ]

    return logs_list, pagination
