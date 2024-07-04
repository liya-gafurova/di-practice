import uuid

from shared.repositories import Repository


class AccountRepository(Repository):
    async def get_all__user(self, user_id: uuid.UUID):
        raise NotImplementedError