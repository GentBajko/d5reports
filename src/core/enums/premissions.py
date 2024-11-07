from enum import Flag, auto


class Permissions(Flag):
    NO_LONGER_EMPLOYED = 0
    MANAGE_USERS = auto()
    VIEW_ALL_PROJECTS = auto()
    VIEW_ALL_TASKS = auto()
    VIEW_ALL_TEAMS = auto()
    CREATE_PROJECTS = auto()
    CREATE_TEAMS = auto()
    ASSIGN_DEVELOPERS_TO_TEAMS = auto()
    VIEW_ASSIGNED_PROJECTS = auto()
    CREATE_TASKS = auto()
    UPDATE_TASKS = auto()
    VIEW_PROJECT_TASKS = auto()

    ADMIN = (
        MANAGE_USERS
        | VIEW_ALL_PROJECTS
        | VIEW_ALL_TASKS
        | VIEW_ALL_TEAMS
        | CREATE_PROJECTS
        | CREATE_TEAMS
        | ASSIGN_DEVELOPERS_TO_TEAMS
    )

    DEVELOPER = (
        VIEW_ASSIGNED_PROJECTS
        | CREATE_TASKS
        | UPDATE_TASKS
        | VIEW_PROJECT_TASKS
    )

    @property
    def name(self) -> str:
        return str(self._name_)

    @property
    def value(self) -> int:
        return self._value_

    def __str__(self):
        if self.name:
            return self.name.replace("_", " ").title()
        return ""

    def __getitem__(self, item):
        return self.__class__[item]

    def array(self):
        return self.__str__().split("|")

    def from_string(self, string: str):
        return self.__class__[string.upper().replace(" ", "_")]
