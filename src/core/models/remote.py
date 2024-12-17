from ulid import ULID


class RemoteDay:
    def __init__(self, user_id: str, day):
        self.id = str(ULID())
        self.user_id = user_id
        self.day = day

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
            "day": self.day.isoformat(),
        }
