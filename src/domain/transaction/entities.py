import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from domain.account.entities import AccountNumber
from domain.category.entities import Category
from shared.entities import Entity


class TransactionType(str, Enum):
    CORRECTION = 'correction'
    TRANSFER = 'transfer'
    INCOME = 'income'
    EXPENSE = 'expense'


@dataclass
class Transaction(Entity):
    user_id: uuid.UUID
    credit_account: AccountNumber | None  # from
    debit_account: AccountNumber | None   # to
    amount: float
    _amount: Decimal = field(init=False, repr=False)
    type: None | TransactionType = None
    category_id: uuid.UUID | None = None
    category: None | Category = None

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value: float | Decimal):
        self._amount = Decimal(value).quantize(Decimal('.01'))
