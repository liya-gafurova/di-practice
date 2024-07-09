import uuid
from decimal import Decimal
from typing import TypeVar

from pydantic import BaseModel

AccountNumber = TypeVar('AccountNumber', bound=str)
TransactionType = TypeVar('TransactionType', bound=str)


class AccountReadModel(BaseModel):
    number: AccountNumber
    name: str | None
    balance: Decimal


class TransactionReadModel(BaseModel):
    credit_account: AccountNumber | None = None
    amount: Decimal
    debit_account: AccountNumber | None = None
    type: TransactionType
