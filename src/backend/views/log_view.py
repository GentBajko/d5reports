from typing import List, Tuple
import datetime

from ulid import ULID

from backend.models import LogCreateModel, LogResponseModel
from core.enums.task_status import TaskStatus
from core.models.log import Log
from database.models import log_mapper  # noqa F401
from core.models.task import Task
from backend.utils.pagination import calculate_pagination
from backend.models.pagination import Pagination
from database.interfaces.session import ISession
from database.repositories.repository import Repository


def create_log(log: LogCreateModel, session: ISession) -> LogResponseModel:
    """
    Create a new log in the database.
    """
    with session as s:
        task_repo = Repository(s, Task)
        task = task_repo.get(id=log.task_id)

        if not task:
            raise ValueError("Task not found")

        repo = Repository(s, Log)

        new_log = Log(
            id=str(ULID()),
            timestamp=int(datetime.datetime.now().timestamp()),
            task_id=log.task_id,
            task_name=task.title,
            description=log.description,
            user_id=task.user_id,
            hours_spent_today=log.hours_spent_today,
            task_status=log.task_status,
        )
        if task._status == TaskStatus.DONE and new_log._task_status != TaskStatus.DONE:
            task.returned = True
        task.hours_worked += log.hours_spent_today
        task.status = log.task_status
        print(task.to_dict())
        task_repo.update(task)

        repo.create(new_log)
        s.commit()
        log_data = new_log.to_dict()
    return LogResponseModel.model_validate(log_data)


def get_log(session: ISession, **kwargs) -> LogResponseModel:
    """
    Retrieve a single log from the database based on provided criteria.
    """
    with session as s:
        print(kwargs)
        repo = Repository[Log](s, Log)
        log = repo.query(**kwargs)
        if not log:
            raise ValueError("Log not found")
        log_obj = log[0]
        log_dict = log_obj.to_dict()
    return LogResponseModel.model_validate(log_dict)


def update_log(
    log_id: str, log_update: LogCreateModel, session: ISession
) -> LogResponseModel:
    """
    Update an existing log's information.
    """
    with session as s:
        repo = Repository[Log](s, Log)
        log = repo.get(id=log_id)
        if not log:
            raise ValueError("Log not found")

        for attr, value in log_update.model_dump().items():
            setattr(log, attr, value)

        task_repo = Repository(s, Task)
        task = task_repo.get(id=log.task_id)
        if task:
            task.hours_worked += log_update.hours_spent_today
            task.status = log_update.task_status
            task_repo.update(task)

        s.commit()
        log_dict = log.to_dict()
    return LogResponseModel.model_validate(log_dict)


def upsert_log(log: LogResponseModel, session: ISession) -> LogResponseModel:
    """
    Insert a new log or update an existing log based on unique constraints.
    """
    with session as s:
        repo = Repository[Log](s, Log)
        existing_log = repo.get(id=log.id)
        if existing_log:
            for attr, value in log.model_dump().items():
                setattr(existing_log, attr, value)
            s.commit()
            log_dict = existing_log.to_dict()
        else:
            new_log = Log(
                id=log.id or str(ULID()),
                timestamp=log.timestamp
                or int(datetime.datetime.now().timestamp()),
                task_id=log.task_id,
                task_name=log.task_name,
                description=log.description,
                user_id=log.user_id,
                hours_spent_today=log.hours_spent_today,
                task_status=log.task_status,
            )
            repo.create(new_log)
            s.commit()
            log_dict = new_log.to_dict()
    return LogResponseModel.model_validate(log_dict)


def get_all_logs(
    session: ISession, pagination: Pagination, **kwargs
) -> Tuple[List[LogResponseModel], Pagination]:
    with session as s:
        repo = Repository(s, Log)
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

        logs = repo.query(
            order_by=pagination.order_by,
            limit=pagination.limit,
            offset=pagination.offset,
            **kwargs,
        )

        logs_list = [
            LogResponseModel.model_validate(log.to_dict()) for log in logs
        ]

    return logs_list, pagination
