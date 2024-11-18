from typing import List

from loguru import logger

from src.backend.models import ProjectCreateModel, ProjectResponseModel
from src.database.models import (
    project_mapper,  # noqa F401
    project_developers_table,
)
from src.core.models.task import Task
from src.core.models.user import User
from src.core.models.project import Project
from src.backend.models.models import TaskResponseModel, UserResponseModel
from src.core.models.project_user import ProjectUser
from src.database.interfaces.session import ISession
from src.backend.utils.populate_fields import populate_project_fields
from src.database.repositories.repository import Repository


def create_project(
    project: ProjectCreateModel, session: ISession
) -> ProjectResponseModel:
    """
    Create a new project in the database.
    """
    ProjectResponseModel.model_rebuild()
    new_project = Project(
        name=project.name,
        email=project.email,
        send_email=project.send_email,
        archived=project.archived,
        developers=[],
        tasks=[],
    )
    with session as s:
        repository = Repository(s, Project)
        created_project = repository.create(new_project)
        project_data = created_project.to_dict()
    return ProjectResponseModel.model_validate(project_data)


def get_project(session: ISession, **kwargs) -> ProjectResponseModel:
    """
    Retrieve a single project from the database based on provided criteria.
    """
    ProjectResponseModel.model_rebuild()
    with session as s:
        repository = Repository(s, Project)
        print(kwargs)
        project = repository.query(**kwargs) if kwargs else repository.query()

        if not project:
            raise ValueError("Project not found")

        project_dict = project[0].to_dict()
        populate_project_fields(project_dict)
    return ProjectResponseModel.model_validate(project_dict)


def update_project(
    project_id: str, project_update: ProjectCreateModel, session: ISession
) -> ProjectResponseModel:
    """
    Update an existing project's information.
    """
    ProjectResponseModel.model_rebuild()
    ProjectCreateModel.model_rebuild()

    with session as s:
        repository = Repository(s, Project)
        existing_project = repository.get(project_id)

        if not existing_project:
            raise ValueError(f"Project with id {project_id} does not exist.")

        project_data = project_update.model_dump(exclude_unset=True)

        for key, value in project_data.items():
            setattr(existing_project, key, value)

        repository.update(existing_project)
        project_dict = existing_project.to_dict()
    return ProjectResponseModel.model_validate(project_dict)


def upsert_project(
    project: ProjectCreateModel, session: ISession
) -> ProjectResponseModel:
    """
    Insert a new project or update an existing project based on unique constraints.
    """
    ProjectResponseModel.model_rebuild()

    with session as s:
        repository = Repository(s, Project)
        existing_project = repository.query(name=project.name)

        if existing_project:
            project_obj = existing_project[0]
            for key, value in project.model_dump(exclude_unset=True).items():
                setattr(project_obj, key, value)
            repository.update(project_obj)
        else:
            project_obj = Project(
                name=project.name,
                email=project.email,
                send_email=project.send_email,
                archived=project.archived,
            )
            repository.create(project_obj)

        project_dict = project_obj.to_dict()

    return ProjectResponseModel.model_validate(project_dict)


def get_all_projects(session: ISession) -> List[ProjectResponseModel]:
    """
    Retrieve all projects from the database.
    """
    ProjectResponseModel.model_rebuild()

    with session as s:
        repository = Repository(s, Project)
        projects = repository.query()
        logger.info(f"{type(projects)}: {projects}")
        project_dicts = [project.to_dict() for project in projects]

        project_dicts = [project.to_dict() for project in projects]
        for project in project_dicts:
            project["developers"] = str(len(project["developers"]))
            project["tasks"] = str(len(project["tasks"]))
            populate_project_fields(project)
    output = [
        ProjectResponseModel.model_validate(proj_dict)
        for proj_dict in project_dicts
    ]
    return output


def get_users_projects(
    user_id: str, session: ISession
) -> List[ProjectResponseModel]:
    """
    Retrieve all projects associated with a user.
    """
    ProjectResponseModel.model_rebuild()

    try:
        with session as s:
            # Get project IDs from association table - fixed WHERE clause
            assoc = Repository(s, ProjectUser)
            result = assoc.query(user_id=user_id)
            print([row.project_id for row in result])
            if not result:
                return []

            project_ids = [row.project_id for row in result]

            repository = Repository(s, Project)
            projects = []
            for project_id in project_ids:
                project = repository.get(project_id)
                print(project)
                if project:
                    projects.append(project)

            project_dicts = [project.to_dict() for project in projects]
            for project in project_dicts:
                populate_project_fields(project)

        return [
            ProjectResponseModel.model_validate(proj_dict)
            for proj_dict in project_dicts
        ]
    except Exception as e:
        logger.error(f"Error retrieving projects: {str(e)}")
        return []


def assign_project_to_user(
    project_id: str, user_id: str, session: ISession
) -> ProjectResponseModel:
    ProjectResponseModel.model_rebuild()
    with session as s:
        project = Repository(s, Project).get(project_id)
        user = Repository(s, User).get(user_id)

        if not project:
            raise ValueError(f"Project with id {project_id} does not exist.")
        if not user:
            raise ValueError(f"User with id {user_id} does not exist.")

        stmt = project_developers_table.insert().values(
            project_id=project_id, user_id=user_id
        )
        s.execute(stmt)
        s.commit()

    return ProjectResponseModel.model_validate(project.to_dict())


def get_user_by_project(
    session: ISession, project_id: str
) -> List[UserResponseModel]:
    """
    Retrieve all users associated with a project.

    This function rebuilds the necessary models, queries the database for all users associated with a
    project, and populates developer fields within the user's associated projects. It then validates
    and returns the user data as a list of `UserResponseModel`.

    Args:
        session (ISession): The database session used for querying the users.
        project_id (str): The unique identifier of the project to filter users.

    Returns:
        List[UserResponseModel]: A list of validated response models representing the users.

    Raises:
        IndexError: If no users are associated with the specified project.
    """
    UserResponseModel.model_rebuild()
    ProjectResponseModel.model_rebuild()

    with session as s:
        assoc = Repository(s, ProjectUser)
        result = assoc.query(project_id=project_id)
        if not result:
            raise IndexError(f"No users associated with project {project_id}.")
        user_ids = [row.user_id for row in result]
        repository = Repository(s, User)
        users: List[User] = []

        for user_id in user_ids:
            user = repository.get(user_id)
            if user:
                users.append(user)

        if not users:
            return []

        user_dicts = [user.to_dict() for user in users]

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


def get_project_tasks(
    session: ISession, project_id: str
) -> List[TaskResponseModel]:
    """
    Retrieve all tasks associated with a project.

    This function rebuilds the necessary models, queries the database for all tasks associated with a
    project, and populates user fields within the task's associated project. It then validates and
    returns the task data as a list of `TaskResponseModel`.

    Args:
        session (ISession): The database session used for querying the tasks.
        project_id (str): The unique identifier of the project to filter tasks.

    Returns:
        List[TaskResponseModel]: A list of validated response models representing the tasks.

    Raises:
        IndexError: If no tasks are associated with the specified project.
    """
    TaskResponseModel.model_rebuild()
    ProjectResponseModel.model_rebuild()

    with session as s:
        repository = Repository(s, Task)
        tasks = repository.query(project_id=project_id)
        if not tasks:
            return []
        task_dicts = [task.to_dict() for task in tasks]

    output = []
    for task_dict in task_dicts:
        for project in task_dict.get("project", []):
            if isinstance(project, dict):
                project.setdefault("tasks", [])
                project["tasks"].append(task_dict)
        output.append(TaskResponseModel.model_validate(task_dict))
    return output
