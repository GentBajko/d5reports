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


def populate_task_fields(task_dict: dict) -> None:
    """
    Populate task dictionary with related fields and logs.

    Args:
        task_dict: Dictionary containing task data
    """
    task_dict.setdefault("title", task_dict.get("title", ""))
    task_dict.setdefault("description", task_dict.get("description", ""))
    task_dict.setdefault("hours_required", task_dict.get("hours_required", 0))
    task_dict.setdefault("status", task_dict.get("status", "Pending"))

    logs = task_dict.get("logs", [])
    for log in logs:
        if isinstance(log, dict):
            log.setdefault("task_name", task_dict.get("title"))
            log.setdefault("task_status", task_dict.get("status"))
            log.setdefault(
                "hours_spent_today", log.get("hours_spent_today", 0)
            )
            log.setdefault("description", log.get("description", ""))
            log.setdefault("timestamp", log.get("timestamp", 0))
            log.setdefault("user_id", task_dict.get("user_id"))
            log.setdefault("task_id", task_dict.get("id"))


def populate_fields(data):
    if isinstance(data, dict):
        if "email" in data and "full_name" in data:
            populate_developer_fields(data)

        if "projects" in data:
            for project in data["projects"]:
                populate_project_fields(project)
                populate_fields(project)

        if "developers" in data:
            for developer in data["developers"]:
                populate_developer_fields(developer)
                populate_fields(developer)

        if "tasks" in data:
            for task in data["tasks"]:
                populate_task_fields(task)
                populate_fields(task)

        if "logs" in data:
            for log in data["logs"]:
                populate_fields(log)
    elif isinstance(data, list):
        for item in data:
            populate_fields(item)
