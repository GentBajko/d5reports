from typing import List

from ulid import ULID


class Projects:
    def __init__(
        self,
        id: str,
        name: str,
        email: str,
        developers: List[str],
        tasks: List[str],
    ):
        self._id = id
        self.name = name
        self.email = email
        self._developers = developers
        self._tasks = tasks

    @property
    def id(self) -> str:
        return ULID.from_str(self._id)

    @property
    def developers(self) -> List[str]:
        return [ULID.from_str(developer) for developer in self._developers]

    @property
    def tasks(self) -> List[str]:
        return [ULID.from_str(task) for task in self._tasks]
