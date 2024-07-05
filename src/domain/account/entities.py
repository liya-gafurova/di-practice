import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from random import random, choices
from typing import TypeVar

from shared.entities import Entity

AccountNumber: TypeVar = TypeVar('AccountNumber', bound=str)
ACCOUNT_NUMBER_LENGTH = 16


@dataclass
class Account(Entity):
    name: None | str
    number: AccountNumber
    owner_id: uuid.UUID
    balance: Decimal | float
    _balance: Decimal = field(init=False, repr=False)

    @classmethod
    def generate_number(cls) -> AccountNumber:
        return ''.join(choices('0123456789', k=ACCOUNT_NUMBER_LENGTH))

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value: float | Decimal):
        self._balance = Decimal(value).quantize(Decimal('.01'))
