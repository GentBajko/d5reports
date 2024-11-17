def populate_developer_fields(user_dict: dict) -> None:
    """
    Populate the developer fields with the user's email, full name, and project tasks.

    :param user_dict: The dictionary representation of the user.
    """
    for project in user_dict.get("projects", []):
        if isinstance(project, dict):
            for developer in project.get("developers", []):
                if isinstance(developer, dict):
                    developer.setdefault("email", user_dict.get("email"))
                    developer.setdefault(
                        "full_name", user_dict.get("full_name")
                    )
                    developer.setdefault("tasks", project.get("tasks", []))


def populate_project_fields(project_dict):
    for developer in project_dict.get("developers", []):
        if isinstance(developer, dict):
            developer.setdefault("email", developer.get("email"))
            developer.setdefault("full_name", developer.get("full_name"))
            developer.setdefault("tasks", developer.get("tasks", []))
            for dev_project in developer.get("projects", []):
                if isinstance(dev_project, dict):
                    dev_project.setdefault("name", project_dict.get("name"))
                    dev_project.setdefault("email", project_dict.get("email"))
                    dev_project.setdefault(
                        "send_email", project_dict.get("send_email")
                    )
                    dev_project.setdefault(
                        "archived", project_dict.get("archived")
                    )
