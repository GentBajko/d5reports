from typing import Any, List, Type, Generic, TypeVar, Optional

from database.interfaces.session import ISession

T = TypeVar("T")


class Repository(Generic[T]):
    def __init__(self, session: ISession, model: Type[T]):
        self.session = session
        self.model = model

    def create(self, obj: T) -> T:
        self.session.add(obj)
        self.session.commit()
        return obj

    def get(self, id: Any) -> Optional[T]:
        return self.session.get(self.model, id)

    def update(self, obj: T) -> T:
        self.session.update(obj)
        self.session.commit()
        return obj

    def delete(self, obj: T) -> None:
        self.session.delete(obj)
        self.session.commit()

    def query(
        self,
        order_by: Optional[List[Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **filters,
    ) -> List[T]:
        return self.session.query(
            self.model,
            order_by=order_by,
            limit=limit,
            offset=offset,
            **filters,
        )

    def count(self, **filters) -> int:
        return self.session.count(self.model, **filters)