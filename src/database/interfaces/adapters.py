from typing import Protocol

from sqlalchemy.engine import Engine


class DatabaseAdapter(Protocol):
    @property
    def engine(self) -> Engine:
        """Returns the SQLAlchemy Engine instance."""
        ...
