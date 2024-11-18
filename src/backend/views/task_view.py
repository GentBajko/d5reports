from typing import List

from src.backend.models import TaskCreateModel, TaskResponseModel
from src.database.models import task_mapper  # noqa F401
from src.core.models.task import Task
from src.database.interfaces.session import ISession
from src.database.repositories.repository import Repository


def create_task(task: TaskCreateModel, session: ISession) -> TaskResponseModel:
    """
    Create a new task in the database.
    """
    TaskResponseModel.model_rebuild()
    new_task = Task(
        project_id=task.project_id,
        project_name=task.project_name,
        user_id=task.user_id,
        title=task.title,
        hours_required=task.hours_required,
        description=task.description,
        status=task.status,
        logs=[],
    )
    with session as s:
        repo = Repository[Task](s, Task)
        repo.create(new_task)
        s.commit()
        task_data = new_task.to_dict()
    return TaskResponseModel.model_validate(task_data)


def get_task(session: ISession, **kwargs) -> TaskResponseModel:
    """
    Retrieve a single task from the database based on provided criteria.
    """
    TaskResponseModel.model_rebuild()
    with session as s:
        repo = Repository[Task](s, Task)
        task = repo.query(**kwargs)
        if not task:
            raise ValueError("Task not found")
        task_dict = task[0].to_dict()
    return TaskResponseModel.model_validate(task_dict)


def update_task(
    task_id: str, task_update: TaskCreateModel, session: ISession
) -> TaskResponseModel:
    """
    Update an existing task's information.
    """
    TaskResponseModel.model_rebuild()
    TaskCreateModel.model_rebuild()

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
    TaskResponseModel.model_rebuild()

    with session as s:
        repo = Repository[Task](s, Task)
        existing_task = repo.get(id=task.id)
        if existing_task:
            for attr, value in task.dict().items():
                setattr(existing_task, attr, value)
            s.commit()
            task_dict = existing_task.to_dict()
        else:
            new_task = Task(
                project_id=task.project_id,
                project_name=task.project_name,
                user_id=task.user_id,
                title=task.title,
                hours_required=task.hours_required,
                description=task.description,
                status=task.status,
                logs=[],
            )
            repo.create(new_task)
            s.commit()
            task_dict = new_task.to_dict()
    return TaskResponseModel.model_validate(task_dict)


def get_all_tasks(session: ISession) -> List[TaskResponseModel]:
    """
    Retrieve all tasks from the database.
    """
    TaskResponseModel.model_rebuild()

    with session as s:
        repo = Repository(s, Task)
        tasks = repo.query()
        tasks_list = [
            TaskResponseModel.model_validate(task.to_dict()) for task in tasks
        ]
    return tasks_list


def get_project_tasks(
    session: ISession, project_id: str
) -> List[TaskResponseModel]:
    """
    Retrieve all tasks associated with a specific project.
    """
    TaskResponseModel.model_rebuild()

    with session as s:
        repo = Repository[Task](s, Task)
        tasks = repo.query(project_id=project_id)
        tasks_list = [
            TaskResponseModel.model_validate(task.to_dict()) for task in tasks
        ]
    return tasks_list


def get_user_tasks(session: ISession, user_id: str) -> List[TaskResponseModel]:
    """
    Retrieve all tasks assigned to a specific user.
    """
    TaskResponseModel.model_rebuild()

    with session as s:
        repo = Repository(s, Task)
        tasks = repo.query(user_id=user_id)
        tasks_list = [
            TaskResponseModel.model_validate(task.to_dict()) for task in tasks
        ]
    return tasks_list
