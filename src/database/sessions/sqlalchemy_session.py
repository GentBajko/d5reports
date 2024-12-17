from typing import Any, Dict, List, Type, TypeVar, Optional

from sqlalchemy.orm import Session, joinedload

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
        options: Optional[List[Any]] = None,
        in_: Optional[Dict[Any, List[Any]]] = None,
        **filters,
    ) -> List[T]:
        query = self._session.query(model)

        if in_:
            in_filters = [
                column.in_(in_values) for column, in_values in in_.items()
            ]
            query = query.filter(*in_filters)

        if filters:
            conditions = self.__get_conditions(model, **filters)
            query = query.filter(*conditions)

        if order_by:
            query = query.order_by(*order_by)

        if limit is not None:
            query = query.limit(limit)

        if offset is not None:
            query = query.offset(offset)

        if options:
            query = query.options(*[joinedload(option) for option in options])

        results = query.all()
        return results


    def execute(self, stmt: Any) -> None:
        self._session.execute(stmt)

    def count(self, model: Type[T], **filters) -> int:
        query = self._session.query(model)
        conditions = self.__get_conditions(model, **filters)

        return query.filter(*conditions).count()

    def __get_conditions(self, model: Type[T], **filters):
        conditions = []
        for key, value in filters.items():
            if "__" in key:
                field_name, op = key.split("__", 1)
                column = getattr(model, field_name, None)
                if column is None:
                    raise AttributeError(
                        f"Model {model} has no attribute '{field_name}'"
                    )

                if op == "gt":
                    conditions.append(column > value)
                elif op == "gte":
                    conditions.append(column >= value)
                elif op == "lt":
                    conditions.append(column < value)
                elif op == "lte":
                    conditions.append(column <= value)
                elif op == "eq":
                    conditions.append(column == value)
                elif op == "contains":
                    conditions.append(column.ilike(f"%{value}%"))  # Case-insensitive
                elif op == "startswith":
                    conditions.append(column.ilike(f"{value}%"))
                elif op == "endswith":
                    conditions.append(column.ilike(f"%{value}"))
                else:
                    raise ValueError(f"Unsupported filter operator: {op}")
            else:
                column = getattr(model, key, None)
                if column is None:
                    raise AttributeError(
                        f"Model {model} has no attribute '{key}'"
                    )
                conditions.append(column == value)
        return conditions

    def __enter__(self) -> "SQLAlchemySession":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._session.close()
