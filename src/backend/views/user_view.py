from typing import List, Tuple, Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from backend.models import (
    UserCreateModel,
    UserResponseModel,
    ProjectResponseModel,
)
from core.models.log import Log
from database.models import user_mapper  # noqa F401
from core.models.task import Task
from core.models.user import User
from core.models.project import Project
from backend.models.models import LogResponseModel, TaskResponseModel
from backend.utils.pagination import calculate_pagination
from core.models.project_user import ProjectUser
from backend.models.pagination import Pagination
from database.interfaces.session import ISession
from database.repositories.repository import Repository


def create_user(user: UserCreateModel, session: ISession) -> UserResponseModel:
    """
    Create a new user in the database.

    This function initializes the user response model, creates a new `User` instance with the provided
    details, and persists it to the database using the provided session. After creation, it validates
    and returns the newly created user as a `UserResponseModel`.

    Args:
        user (UserCreateModel): An instance containing the user's creation data.
        session (ISession): The database session used for interacting with the database.

    Returns:
        UserResponseModel: A validated response model representing the newly created user.
    """
    ph = PasswordHasher()
    hashed_password = ph.hash(user.password)
    new_user = User(
        email=user.email,
        full_name=user.full_name,
        password=hashed_password,
        permissions=user.permissions,
        projects=[],
        tasks=[],
    )
    with session as s:
        repository = Repository(s, User)
        created_user = repository.create(new_user)
        user_data = created_user.to_dict()
    return UserResponseModel.model_validate(user_data)


def authenticate_user(
    email: str, password: str, session: ISession
) -> Optional[User]:
    with session as s:
        repository = Repository(s, User)
        users = repository.query(email=email)
        if not users:
            return None
        user = users[0]
        ph = PasswordHasher()
        try:
            ph.verify(user.password, password)
            return user
        except VerifyMismatchError:
            return None


def get_user(session: ISession, **kwargs) -> UserResponseModel:
    """
    Retrieve a single user from the database based on provided criteria.

    This function rebuilds the project and user response models, queries the database for a user
    matching the provided keyword arguments, and populates developer fields within the user's
    associated projects. It then validates and returns the user data as a `UserResponseModel`.

    Args:
        session (ISession): The database session used for querying the user.
        **kwargs: Arbitrary keyword arguments representing the query parameters to filter the user.

    Returns:
        UserResponseModel: A validated response model representing the retrieved user.

    Raises:
        IndexError: If no user matches the provided criteria.
    """
    with session as s:
        repository = Repository(s, User)
        user = repository.query(**kwargs)[0]
        user_dict = user.to_dict()

    return UserResponseModel.model_validate(user_dict)


def update_user(
    user_id: str, user_update: UserCreateModel, session: ISession
) -> UserResponseModel:
    """
    Update an existing user's information.

    This function rebuilds the necessary models, retrieves the existing user by `user_id`, and updates
    the user's attributes with the provided `user_update` data. It then persists the changes to the
    database, populates developer fields, and returns the updated user as a `UserResponseModel`.

    Args:
        user_id (str): The unique identifier of the user to update.
        user_update (UserCreateModel): An instance containing the updated user data.
        session (ISession): The database session used for interacting with the database.

    Returns:
        UserResponseModel: A validated response model with the updated user data.

    Raises:
        ValueError: If a user with the specified `user_id` does not exist.
    """
    with session as s:
        repository = Repository(s, User)
        existing_user = repository.get(user_id)

        if not existing_user:
            raise ValueError(f"User with id {user_id} does not exist.")

        user_data = user_update.model_dump(exclude_unset=True)

        if "password" in user_data:
            ph = PasswordHasher()
            user_data["password"] = ph.hash(user_data["password"])

        for key, value in user_data.items():
            setattr(existing_user, key, value)

        repository.update(existing_user)

    return UserResponseModel.model_validate(existing_user.to_dict())


def upsert_user(user: UserCreateModel, session: ISession) -> UserResponseModel:
    """
    Insert a new user or update an existing user based on unique constraints.

    This function attempts to find an existing user by unique fields (e.g., email). If the user exists,
    it updates the user's attributes with the provided data. If the user does not exist, it creates a
    new user. After upserting, it populates developer fields and returns the user as a
    `UserResponseModel`.

    Args:
        user (UserCreateModel): An instance containing the user data for upserting.
        session (ISession): The database session used for interacting with the database.

    Returns:
        UserResponseModel: A validated response model with the upserted user data.
    """
    with session as s:
        repository = Repository(s, User)
        existing_user = repository.query(email=user.email)

        if existing_user:
            user_obj = existing_user[0]
            for key, value in user.model_dump(exclude_unset=True).items():
                setattr(user_obj, key, value)
            repository.update(user_obj)
        else:
            user_obj = User(
                email=user.email,
                full_name=user.full_name,
                password=user.password,
                permissions=user.permissions,
            )
            repository.create(user_obj)

    return UserResponseModel.model_validate(user_obj.to_dict())


def get_all_users(
    session: ISession, pagination: Pagination, **kwargs
) -> Tuple[List[UserResponseModel], Pagination]:
    with session as s:
        repository = Repository(s, User)
        total = repository.count(**kwargs)

        order_by = pagination.order_by

        pagination = calculate_pagination(
            total=total,
            page=pagination.current_page or 1,
            per_page=pagination.limit or 15,
        )

        pagination.order_by = order_by

        if total == 0:
            return [], pagination

        query = repository.query(
            order_by=pagination.order_by,
            limit=pagination.limit,
            offset=pagination.offset,
            options=[User.tasks, User.projects],  # type: ignore
            **kwargs,
        )

        user_models = [
            UserResponseModel.model_validate(user.to_dict()) for user in query
        ]
        return user_models, pagination


def get_user_tasks(
    session: ISession, user_id: str, pagination: Pagination
) -> Tuple[List[TaskResponseModel], Pagination]:
    """
    Retrieve all tasks associated with a user.

    This function rebuilds the necessary models, queries the database for all tasks associated with a
    user, and populates user fields within the task's associated project. It then validates and
    returns the task data as a list of `TaskResponseModel`.

    Args:
        session (ISession): The database session used for querying the tasks.
        user_id (str): The unique identifier of the user to filter tasks.

    Returns:
        List[TaskResponseModel]: A list of validated response models representing the tasks.
    """
    with session as s:
        repository = Repository(s, Task)
        tasks = repository.query(user_id=user_id)

        total = len(tasks)

        order_by = pagination.order_by

        pagination = calculate_pagination(
            total=total,
            page=pagination.current_page or 1,
            per_page=pagination.limit or 15,
        )

        pagination.order_by = order_by

        if not tasks or total == 0:
            return [], pagination

        task_dicts = [task.to_dict() for task in tasks]

    output = [
        TaskResponseModel.model_validate(task_dict) for task_dict in task_dicts
    ]

    return output, pagination


def get_project_by_user(
    session: ISession, user_id: str, pagination: Pagination, **kwargs
) -> Tuple[List[ProjectResponseModel], Pagination]:
    """
    Retrieve paginated projects associated with a user.

    Args:
        session (ISession): The database session used for querying the projects.
        user_id (str): The unique identifier of the user to filter projects.
        pagination (Pagination): Pagination parameters.

    Returns:
        Tuple[List[ProjectResponseModel], Pagination]: Tuple of project list and pagination info.

    Raises:
        IndexError: If no projects are associated with the specified user.
    """
    with session as s:
        repository = Repository(s, Project)
        project_user_repository = Repository(s, ProjectUser)

        total = project_user_repository.count(user_id=user_id, **kwargs)
        project_ids = [
            association.project_id
            for association in project_user_repository.query(
                user_id=user_id, **kwargs
            )
        ]

        order_by = pagination.order_by

        pagination = calculate_pagination(
            total=total,
            page=pagination.current_page or 1,
            per_page=pagination.limit or 15,
        )

        pagination.order_by = order_by

        if total == 0:
            return [], pagination

        projects = repository.query(
            order_by=pagination.order_by,
            limit=pagination.limit,
            offset=pagination.offset,
            in_={Project.id: project_ids},  # type: ignore
            **kwargs,
        )

        if not projects:
            return [], pagination

        project_dicts = [project.to_dict() for project in projects]

    output = [
        ProjectResponseModel.model_validate(project)
        for project in project_dicts
    ]

    return output, pagination

def get_user_logs(
    session: ISession, user_id: str, pagination: Pagination, **kwargs
) -> Tuple[List[LogResponseModel], Pagination]:
    with session as s:
        repo = Repository(s, Log)
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

        logs = repo.query(
            user_id=user_id,
            order_by=pagination.order_by,
            limit=pagination.limit,
            offset=pagination.offset,
            **kwargs,
        )

        logs_list = [
            LogResponseModel.model_validate(log.to_dict()) for log in logs
        ]

    return logs_list, pagination

