import uuid
from dataclasses import dataclass

from shared.entities import Entity


@dataclass
class Category(Entity):
    name: str
    user_id: uuid.UUID | None
