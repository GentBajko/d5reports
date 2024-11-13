from typing import List

from src.backend.models import (
    ProjectCreateModel,
    ProjectResponseModel,
    UserResponseModel,
)
from src.database.models import project_mapper  # noqa F401
from src.core.models.project import Project
from src.database.interfaces.session import ISession
from src.database.repositories.repository import Repository


def create_project(
    project: ProjectCreateModel, session: ISession
) -> ProjectResponseModel:
    """
    Create a new project in the database.

    Args:
        project (ProjectCreateModel): An instance containing the project's creation data.
        session (ISession): The database session used for interacting with the database.

    Returns:
        ProjectResponseModel: A validated response model representing the newly created project.
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

    Args:
        session (ISession): The database session used for querying the project.
        **kwargs: Arbitrary keyword arguments representing the query parameters to filter the project.

    Returns:
        ProjectResponseModel: A validated response model representing the retrieved project.

    Raises:
        IndexError: If no project matches the provided criteria.
    """
    ProjectResponseModel.model_rebuild()
    UserResponseModel.model_rebuild()
    with session as s:
        repository = Repository(s, Project)
        project = repository.query(**kwargs)[0]
        project_dict = project.to_dict()

    for developer in project_dict.get("developers", []):
        if isinstance(developer, dict):
            developer.setdefault("email", developer.get("email"))
            developer.setdefault("full_name", developer.get("full_name"))
            developer.setdefault("tasks", developer.get("tasks", []))

    return ProjectResponseModel.model_validate(project_dict)


def update_project(
    project_id: str, project_update: ProjectCreateModel, session: ISession
) -> ProjectResponseModel:
    """
    Update an existing project's information.

    Args:
        project_id (str): The unique identifier of the project to update.
        project_update (ProjectCreateModel): An instance containing the updated project data.
        session (ISession): The database session used for interacting with the database.

    Returns:
        ProjectResponseModel: A validated response model with the updated project data.

    Raises:
        ValueError: If a project with the specified `project_id` does not exist.
    """
    ProjectResponseModel.model_rebuild()
    ProjectCreateModel.model_rebuild()

    with session as s:
        repository = Repository(s, Project)
        existing_project = repository.get(project_id)
        if not existing_project:
            raise ValueError(f"Project with id {project_id} does not exist.")

        for key, value in project_update.model_dump(exclude_unset=True).items():
            setattr(existing_project, key, value)

        repository.update(existing_project)

        project_dict = existing_project.to_dict()

    return ProjectResponseModel.model_validate(project_dict)


def upsert_project(
    project: ProjectCreateModel, session: ISession
) -> ProjectResponseModel:
    """
    Insert a new project or update an existing project based on unique constraints.

    Args:
        project (ProjectCreateModel): An instance containing the project data for upserting.
        session (ISession): The database session used for interacting with the database.

    Returns:
        ProjectResponseModel: A validated response model with the upserted project data.
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
                developers=[],
                tasks=[],
            )
            repository.create(project_obj)

        project_dict = project_obj.to_dict()

    return ProjectResponseModel.model_validate(project_dict)


def get_all_projects(session: ISession) -> List[ProjectResponseModel]:
    """
    Retrieve all projects from the database.

    Args:
        session (ISession): The database session used for querying projects.

    Returns:
        List[ProjectResponseModel]: A list of validated response models representing all projects.
    """
    ProjectResponseModel.model_rebuild()

    with session as s:
        repository = Repository(s, Project)
        projects = repository.query()
        project_dicts = [project.to_dict() for project in projects]

    for project_dict in project_dicts:
        for developer in project_dict.get("developers", []):
            if isinstance(developer, dict):
                developer.setdefault("email", developer.get("email"))
                developer.setdefault("full_name", developer.get("full_name"))
                developer.setdefault("tasks", developer.get("tasks", []))

    return [
        ProjectResponseModel.model_validate(project_dict) for project_dict in project_dicts
    ]