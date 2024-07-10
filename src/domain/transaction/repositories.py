import uuid

from domain.account.entities import AccountNumber
from domain.transaction.entities import Transaction
from shared.repositories import Repository


class TransactionRepository(Repository):

    async def get_user_transactions(self, user_id: uuid.UUID) -> list[Transaction]:
        raise NotImplementedError

    async def get_account_transactions(self, account_number: AccountNumber) -> list[Transaction]:
        raise NotImplementedError