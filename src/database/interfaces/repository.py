from typing import Any, List, Optional, Type, Protocol


class IRepository(Protocol):
    @property
    def model(self) -> Type[object]:
        """Returns the model class associated with the repository."""
        ...

    def create(self, *args, **kwargs):
        """Creates a new record in the database."""
        ...

    def get(self, *args, **kwargs):
        """Reads a record from the database."""
        ...

    def update(self, *args, **kwargs):
        """Updates a record in the database."""
        ...

    def upsert(self, *args, **kwargs):
        """Creates a new record or updates an existing one in the database."""
        ...

    def delete(self, *args, **kwargs):
        """Deletes a record from the database."""
        ...

    def query(
        self,
        order_by: Optional[List[Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **filters,
    ): ...