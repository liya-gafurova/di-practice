import uuid

from shared.repositories import Repository


class CategoryRepository(Repository):
    async def get_categories(self, user_id: uuid.UUID, with_general: bool = True):
        raise NotImplementedError