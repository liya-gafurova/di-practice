import uuid
from dataclasses import dataclass
from random import random, choices
from typing import TypeVar

from shared.entities import Entity

AccountNumber: TypeVar = TypeVar('AccountNumber', bound=str)
ACCOUNT_NUMBER_LENGTH = 16


@dataclass
class Account(Entity):
    name: None | str
    number: str
    owner_id: uuid.UUID

    @classmethod
    def generate_number(cls):
        return ''.join(choices('0123456789', k=ACCOUNT_NUMBER_LENGTH))
