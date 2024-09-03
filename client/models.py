import uuid
from decimal import Decimal
from typing import TypeVar

from pydantic import BaseModel, Field, ConfigDict

AccountNumber = TypeVar('AccountNumber', bound=str)
TransactionType = TypeVar('TransactionType', bound=str)


class AccountReadModel(BaseModel):
    number: AccountNumber
    name: str | None
    balance: Decimal


class TransactionReadModel(BaseModel):
    credit_account: AccountNumber | None = Field(None, alias='from')
    amount: Decimal
    debit_account: AccountNumber | None = Field(None, alias='to')
    type: TransactionType
    category: None | str = None

    model_config = ConfigDict(populate_by_name=True)
