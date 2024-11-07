from typing import Protocol

from sqlalchemy.engine import Engine


class IDatabaseAdapter(Protocol):
    @property
    def engine(self) -> Engine:
        """Returns the SQLAlchemy Engine instance."""
        ...

    def session(self):
        """Returns a new SQLAlchemy Session instance."""
        ...
