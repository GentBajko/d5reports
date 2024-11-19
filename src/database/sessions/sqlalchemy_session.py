from typing import Any, List, Type, TypeVar, Optional

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

    def query(
        self,
        model: Type[T],
        order_by: Optional[List[Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **filters,
    ) -> List[T]:
        query = self._session.query(model)

        if filters:
            query = query.filter_by(**filters)

        if order_by:
            query = query.order_by(*order_by)

        if limit is not None:
            query = query.limit(limit)

        if offset is not None:
            query = query.offset(offset)

        return query.all()

    def execute(self, stmt: Any) -> None:
        self._session.execute(stmt)

    def count(self, model: Type[T], **filters) -> int:
        return self._session.query(model).filter_by(**filters).count()

    def __enter__(self) -> "SQLAlchemySession":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._session.close()
