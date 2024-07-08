import uuid

from shared.repositories import Repository


class AccountRepository(Repository):
    async def get_all__user(self, user_id: uuid.UUID):
        raise NotImplementedError

    async def calculate_balance(self, account_id: uuid.UUID):
        raise NotImplementedError