from typing import List

from src.backend.models import ProjectCreateModel, ProjectResponseModel
from src.database.models import project_mapper  # noqa F401
from src.core.models.user import User
from src.core.models.project import Project
from src.database.interfaces.session import ISession
from src.backend.utils.populate_fields import populate_project_fields
from src.database.repositories.repository import Repository
from src.database.models.association_tables import project_developers_table


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
        project = repository.query(**kwargs)[0]
        project_dict = project.to_dict()
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

    with session as s:
        user = Repository(s, User).get(user_id)

        if not user:
            raise ValueError(f"User with id {user_id} does not exist.")

        projects = user.projects
        if not projects:
            return []

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
