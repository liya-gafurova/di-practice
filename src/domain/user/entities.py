from dataclasses import dataclass

from shared.entities import Entity


@dataclass
class User(Entity):
    name: str
    email: str | None
