import uuid


class ItemName(str):
    def __new__(self, uuid):
        return str(uuid)

    @classmethod
    def create(cls):
        return cls(uuid.uuid4())

    @classmethod
    def parse(cls, s):
        return cls(uuid.UUID(s))
