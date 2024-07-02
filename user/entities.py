from dataclasses import dataclass

from domain import BaseEntity


@dataclass
class User(BaseEntity):
    name: str
    email: str | None
