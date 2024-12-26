from typing import TYPE_CHECKING

from ulid import ULID


class OfficeCalendar:
    if TYPE_CHECKING:
        id: str
        user_id: str
        day: str
        present: bool

    def __init__(self, user_id: str, day):
        self.id = str(ULID())
        self.user_id = user_id
        self.day = day
        self.present = False

    @property
    def _id(self):
        return ULID.from_str(self.id)

    @property
    def _user_id(self):
        return ULID.from_str(self.user_id)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "day": self.day,
        }
