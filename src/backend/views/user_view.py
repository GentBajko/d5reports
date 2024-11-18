from typing import List, Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from src.backend.models import (
    UserCreateModel,
    UserResponseModel,
    ProjectResponseModel,
)
from src.database.models import user_mapper  # noqa F401
from src.core.models.task import Task
from src.core.models.user import User
from src.core.models.project import Project
from src.backend.models.models import TaskResponseModel
from src.core.models.project_user import ProjectUser
from src.database.interfaces.session import ISession
from src.backend.utils.populate_fields import (
    populate_project_fields,
    populate_developer_fields,
)
from src.database.repositories.repository import Repository


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
    UserResponseModel.model_rebuild()
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
    ProjectResponseModel.model_rebuild()
    UserResponseModel.model_rebuild()
    with session as s:
        repository = Repository(s, User)
        user = repository.query(**kwargs)[0]
        user_dict = user.to_dict()

    for project in user_dict.get("projects", []):
        if isinstance(project, dict):
            for developer in project.get("developers", []):
                if isinstance(developer, dict):
                    developer.setdefault("email", user.email)
                    developer.setdefault("full_name", user.full_name)
                    developer.setdefault("tasks", project.get("tasks", []))

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
    UserResponseModel.model_rebuild()
    UserCreateModel.model_rebuild()

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
        user_dict = existing_user.to_dict()
        populate_developer_fields(user_dict)
    return UserResponseModel.model_validate(user_dict)


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
    UserResponseModel.model_rebuild()

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

        user_dict = user_obj.to_dict()
        populate_developer_fields(user_dict)

    return UserResponseModel.model_validate(user_dict)


def get_all_users(session: ISession, **kwargs) -> List[UserResponseModel]:
    """
    Retrieve users from the database.

    If no keyword arguments are provided, it retrieves all users.
    If keyword arguments are provided, it filters the query using them.

    Args:
        session (ISession): The database session used for querying users.
        **kwargs: Arbitrary keyword arguments for filtering users.

    Returns:
        List[UserResponseModel]: A list of validated response models representing the users.
    """
    UserResponseModel.model_rebuild()

    with session as s:
        repository = Repository(s, User)
        query = repository.query(**kwargs)
        user_dicts = [user.to_dict() for user in query]

    output = []
    for user_dict in user_dicts:
        for project in user_dict.get("projects", []):
            if isinstance(project, dict):
                for developer in project.get("developers", []):
                    if isinstance(developer, dict):
                        developer.setdefault("email", user_dict.get("email"))
                        developer.setdefault(
                            "full_name", user_dict.get("full_name")
                        )
                        developer.setdefault("tasks", project.get("tasks", []))
                        developer.setdefault(
                            "permissions", user_dict.get("permissions")
                        )
        output.append(UserResponseModel.model_validate(user_dict))
    return output


def get_user_tasks(session: ISession, user_id: str) -> List[TaskResponseModel]:
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
    TaskResponseModel.model_rebuild()
    ProjectResponseModel.model_rebuild()

    with session as s:
        repository = Repository(s, Task)
        tasks = repository.query(user_id=user_id)
        if not tasks:
            return []
        task_dicts = [task.to_dict() for task in tasks]

    output = []
    for task_dict in task_dicts:
        for project in task_dict.get("logs", []):
            if isinstance(project, dict):
                project.setdefault("logs", [])
        output.append(TaskResponseModel.model_validate(task_dict))
    return output


def get_project_by_user(
    session: ISession, user_id: str
) -> List[ProjectResponseModel]:
    """
    Retrieve all projects associated with a user.

    This function rebuilds the necessary models, queries the database for all projects associated with a
    user, and populates developer fields within the project's associated users. It then validates and
    returns the project data as a list of `ProjectResponseModel`.

    Args:
        session (ISession): The database session used for querying the projects.
        user_id (str): The unique identifier of the user to filter projects.

    Returns:
        List[ProjectResponseModel]: A list of validated response models representing the projects.

    Raises:
        IndexError: If no projects are associated with the specified user.
    """
    ProjectResponseModel.model_rebuild()
    UserResponseModel.model_rebuild()

    with session as s:
        assoc = Repository(s, ProjectUser)
        result = assoc.query(user_id=user_id)
        if not result:
            raise IndexError(f"No projects associated with user {user_id}.")
        project_ids = [row.project_id for row in result]

        repository = Repository(s, Project)
        projects: List[Project] = []

        for project_id in project_ids:
            project = repository.get(project_id)

            if project:
                projects.append(project)

        if not projects:
            return []

        project_dicts = [project.to_dict() for project in projects]

    output = []
    for project_dict in project_dicts:
        for developer in project_dict.get("developers", []):
            if isinstance(developer, dict):
                developer.setdefault("tasks", project_dict.get("tasks", []))

        populate_project_fields(project_dict)
        print(project_dict)
        output.append(ProjectResponseModel.model_validate(project_dict))
    return output
