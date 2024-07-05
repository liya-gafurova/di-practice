import uuid

from domain.transaction.entities import Transaction
from shared.repositories import Repository


class TransactionRepository(Repository):

    async def get_user_transactions(self, user_id: uuid.UUID) -> list[Transaction]:
        raise NotImplementedError