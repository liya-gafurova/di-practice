import uuid
from decimal import Decimal

from domain.account.entities import Account
from shared.repositories import Repository


class AccountRepository(Repository):
    async def share_access(self, account_id: uuid.UUID, user_id: uuid.UUID):
        raise NotImplementedError

    async def get_all__user(self, user_id: uuid.UUID) -> list[Account]:
        raise NotImplementedError

    async def calculate_balance(self, account_id: uuid.UUID):
        raise NotImplementedError

    async def update_balance(self, account: Account):
        raise NotImplementedError

    async def get_by_number(self, number: str, user_id: uuid.UUID):
        raise NotImplementedError

    async def get_user_account_by_id(self, id: uuid.UUID, user_id: uuid.UUID):
        raise NotImplementedError
