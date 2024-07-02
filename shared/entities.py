import uuid
from dataclasses import dataclass


@dataclass
class Entity:
    id: uuid.UUID

    @classmethod
    def next_id(cls):
        return uuid.uuid4()