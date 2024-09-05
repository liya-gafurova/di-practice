from shared.repositories import Repository


class UserRepository(Repository):
    async def get_by_name(self, name: str):
        raise NotImplementedError