from dataclasses import dataclass

from shared.entities import BaseEntity


@dataclass
class User(BaseEntity):
    name: str
    email: str | None
