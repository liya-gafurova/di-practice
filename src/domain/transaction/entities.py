import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from shared.entities import Entity


@dataclass
class Transaction(Entity):
    user_id: uuid.UUID
    credit_account: uuid.UUID | None  # from
    debit_account: uuid.UUID | None   # to
    amount: float
    _amount: Decimal = field(init=False, repr=False)

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value: float):
        self._amount = Decimal(value).quantize(Decimal('.01'))
