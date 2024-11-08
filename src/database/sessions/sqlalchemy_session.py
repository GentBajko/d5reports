from typing import Any, List, Optional, Type, TypeVar
from sqlalchemy.orm import Session

from database.interfaces.session import ISession

T = TypeVar("T")

class SQLAlchemySession(ISession):
    def __init__(self, session: Session):
        self._session = session

    def add(self, obj: object) -> None:
        self._session.add(obj)

    def get(self, model: Type[T], id: Any) -> Optional[T]:
        return self._session.query(model).get(id)

    def update(self, obj: object) -> None:
        self._session.merge(obj)

    def delete(self, obj: object) -> None:
        self._session.delete(obj)

    def commit(self) -> None:
        try:
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise e

    def rollback(self) -> None:
        self._session.rollback()

    def query(self, model: Type[T], *args, **kwargs) -> List[T]:
        return self._session.query(model).filter_by(*args, **kwargs).all()
