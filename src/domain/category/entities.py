import uuid
from dataclasses import dataclass

from shared.entities import Entity


@dataclass
class Category(Entity):
    name: str
    user_id: uuid.UUID | None

    def is_available_for_user(self, request_user: uuid.UUID):
        return self.user_id is None or self.user_id and self.user_id == request_user
